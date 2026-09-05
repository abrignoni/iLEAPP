__artifacts_v2__ = {
    "whatsAppLogSessions": {
        "name": "WhatsApp - Log Sessions",
        "description": "One row per WhatsApp log file, with the time the log was started, the process that wrote "
                       "it, the device model, iOS and WhatsApp versions, the account JID and the device time zone "
                       "the log recorded.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-05",
        "last_update_date": "2026-09-05",
        "requirements": "none",
        "category": "WhatsApp",
        "notes": "Read from the whatsapp-<date>-<time>-<process>-<n>[-launch].log files under the shared "
                 "app group's Logs folder (WhatsApp_2, MainApp_2, ServiceExtension_2, ShareExtension_2 and Intents_2 on the "
                 "tested images) and, on the iOS 12, 13 and 14 images, under the app's own Library/Logs, including the "
                 "whatsapp-secondary-payments-<date> files WhatsApp writes beside them. The file name carries "
                 "the date and time the log was opened on the device clock, reported as stored in Log Start "
                 "(as stored); on the 66 header-bearing files of two tested images the first line's time "
                 "matched the name's time to the second, while the first line of a secondary-payments log fell "
                 "up to hours from its name's time on 28 of 29. Log lines carry a time of day only. A main-process "
                 "launch log records the device's zone once, as Time zone: Local Time Zone (<IANA zone> (<abbr>) "
                 "offset <seconds>): Time Zone is that text as stored, and Log Start (UTC) is the name's time "
                 "less that offset, filled only for logs that carry the line (31 of 95 files on two tested "
                 "images, all of them WhatsApp launch logs); the offset equalled the named zone's UTC offset in "
                 "seconds on every such line. Last Line Time (as stored) is the time of day on the last "
                 "timestamped line, with no date and no zone. Device, iOS Version, WhatsApp Version, Build Hash, "
                 "Account JID and Launch ID come from the Device: | System: | WhatsApp version: | Hash: | JID: | "
                 "launchID: header the main process and its extensions write at the top of a log (66 of 95 "
                 "files on two tested images; the secondary-payments logs carry none). Account JID is as stored: "
                 "WhatsApp masks all but the last digits in some logs and omits it in others, so a blank or a "
                 "masked value does not mean no account. Log Kind is the process and launch marker from the file "
                 "name. WhatsApp is closed source; nothing here is interpreted beyond the labels the log itself "
                 "carries, and the body lines (network, storage, call-manager and notification tags) are not "
                 "parsed. A row records that the named process started writing a log at Log Start with that "
                 "account signed in; it does not by itself say who used the device.",
        "paths": ('*/Logs/*whatsapp-*.log',),
        "output_types": "standard",
        "artifact_icon": "file-text",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 54 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 0 rows",
            "belkactf6": "0 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 0 rows",
            "ctf2020_ios12": "iOS 12.4 | 5 rows",
            "dexter_ios18": "iOS 18.3.2 | 6 rows",
            "falken_ios26": "iOS 26.2.1 | 0 rows",
            "felix23_ios16": "iOS 16.5 | 41 rows",
            "felix_ios17": "iOS 17.6.1 | 3 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 22 rows",
            "hc_ios26": "iOS 26.5.2 | 0 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 2 rows",
            "hickman_ios14": "iOS 14.3 | 5 rows",
            "hickman_ios15": "iOS 15.3.1 | 11 rows",
            "iphone11_ios17": "iOS 17.3 | 7 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 0 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 3 rows",
            "otto_ios17": "iOS 17.5.1 | 74 rows",
        },
    },
}

import os
import re
from datetime import datetime, timedelta, timezone

from scripts.ilapfuncs import artifact_processor, logfunc

_NAME = re.compile(r'^whatsapp-(?:secondary-payments-)?(\d{4}-\d{2}-\d{2})-(\d{2})-(\d{2})-(\d{2})-(\d{3})-([A-Za-z]+)-(\d+)(-launch)?\.log$')
_LINE_TIME = re.compile(r'^(\d{2}:\d{2}:\d{2}\.\d{3}) ')
_ZONE = re.compile(r'Time zone: Local Time Zone \((.+?) offset (-?\d+)(?: \((\w+)\))?\)')
_HEADER_KEYS = ('Device', 'System', 'WhatsApp version', 'Hash', 'JID', 'launchID')


def _header(lines):
    for line in lines[:6]:
        if line.startswith('Device:'):
            fields = {}
            for part in line.split(' | '):
                key, _, value = part.partition(':')
                if key.strip() in _HEADER_KEYS:
                    fields[key.strip()] = value.strip()
            return fields
    return {}


def _read(path):
    try:
        with open(path, encoding='utf-8', errors='replace') as fh:
            return fh.read().splitlines()
    except OSError as error:
        logfunc(f'WhatsApp log sessions: could not read {os.path.basename(path)}: {error}')
        return None


@artifact_processor
def whatsAppLogSessions(context):
    data_headers = (
        ('Log Start (UTC)', 'datetime'),
        'Log Start (as stored)',
        'Last Line Time (as stored)',
        'Log Kind',
        'Device',
        'iOS Version',
        'WhatsApp Version',
        'Build Hash',
        'Account JID (as stored)',
        'Launch ID',
        'Time Zone (as stored)',
        'Lines',
        'Size Bytes',
        'Source File',
    )
    data_list = []
    sources = []
    seen = set()
    for file_found in context.get_files_found():
        file_found = str(file_found)
        base = os.path.basename(file_found)
        if os.path.isdir(file_found) or base.startswith('._') or file_found in seen:
            continue
        m = _NAME.match(base)
        if not m:
            continue
        seen.add(file_found)
        lines = _read(file_found)
        if lines is None:
            continue
        day, hour, minute, second, milli, process, _number, launch = m.groups()
        started = f'{day} {hour}:{minute}:{second}.{milli}'
        kind = process + (' launch' if launch else '')
        if base.startswith('whatsapp-secondary-payments-'):
            kind = 'secondary-payments ' + kind
        fields = _header(lines)
        zone_text = ''
        started_utc = ''
        for line in lines:
            z = _ZONE.search(line)
            if z:
                zone_text = z.group(0)[len('Time zone: '):]
                try:
                    local = datetime.strptime(started, '%Y-%m-%d %H:%M:%S.%f')
                    started_utc = (local - timedelta(seconds=int(z.group(2)))).replace(tzinfo=timezone.utc)
                except (ValueError, OverflowError):
                    started_utc = ''
                break
        stamps = [t.group(1) for t in (_LINE_TIME.match(line) for line in lines) if t]
        data_list.append((
            started_utc,
            started,
            stamps[-1] if stamps else '',
            kind,
            fields.get('Device', ''),
            fields.get('System', ''),
            fields.get('WhatsApp version', ''),
            fields.get('Hash', ''),
            fields.get('JID', ''),
            fields.get('launchID', ''),
            zone_text,
            len(lines),
            os.path.getsize(file_found),
            context.get_relative_path(file_found),
        ))
        sources.append(file_found)
    return data_headers, data_list, '\n'.join(sources)
