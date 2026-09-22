__artifacts_v2__ = {
    "signalLogLaunches": {
        "name": "Signal - App Launches (logs)",
        "description": "One row per version block the Signal app, its notification service extension or its share "
                       "extension wrote to its debug log at launch: first, last and current app versions, iOS version, "
                       "device model and locale, where the block carries them, as stored.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-05",
        "last_update_date": "2026-09-05",
        "requirements": "none",
        "category": "Signal",
        "notes": "Read from the CocoaLumberjack debug logs Signal keeps in Library/Caches/Logs (main app) and in "
                 "the shared app group's NSELogs and ShareExtensionLogs folders, named "
                 "org.whispersystems.signal[.SignalNSE|.shareextension] <UTC creation time>.log. Each process logs "
                 "its AppVersion block at launch (in Signal-iOS 8.27.0.1843, AppVersion.dumpToLog called from "
                 "AppDelegate.swift line 233, fields in SignalServiceKit/Util/AppVersion.swift), a run of lines "
                 "beginning with firstAppVersion; a row is that block, timed by its first line. The file name is "
                 "written in UTC (DDLogFileManagerDefault's file date formatter is GMT+0 in CocoaLumberjack 3.6.0, "
                 "3.7.0 and 3.9.1), while line timestamps are UTC only from CocoaLumberjack 3.7.0 "
                 "(DDLogFileFormatterDefault in DDFileLogger.m sets no time zone in 3.6.0 and GMT+0 in 3.7.0; "
                 "Signal 3.6.1.4 bundled 3.6.0 and Signal 5.3.1.0 bundled 3.7.0, each scrubbing through a subclass "
                 "of that default formatter, and Signal's own LogFormatter at 8.27.0.1843 also sets GMT+0). Log "
                 "Clock Offset (s) is the log's first line minus its file-name time, zero within a minute and "
                 "otherwise rounded to a quarter hour, and Launch Time subtracts it; on the 44 logs of the tested "
                 "images it was 0 on 41 and -14400 on the three 2020 logs of one image written by Signal 3.6.1, "
                 "and it holds one value per image. Launch Time (as stored) is the line text. On the 23 tested "
                 "images 15 held Signal version blocks and one image's single log held none, 46 blocks in all (33 "
                 "main app, 11 notification service extension, 2 share extension). Values are reported as stored: "
                 "Current App Version is the block's currentAppReleaseVersion where printed (the 11 blocks from "
                 "5.26 to 6.30) and otherwise its currentAppVersion, an underscore-joined version_build value on "
                 "33 of the 46 blocks and a dotted release version on 11, blank on 2; Current Build is filled only "
                 "by the 2022 and 2023 logs that print currentAppBuildVersion, blank on 35 of 46; Last App Version "
                 "was blank on 5 blocks, Build Date/Time on 13, Signal Commit on 24 and Database Corruption on 8, "
                 "and the 2020 to 2022 blocks print (null) where a value was unset. Where present, Last App "
                 "Version equalled Current App Version or Last Completed Launch (main app) on each of the 41 "
                 "blocks that carried it. iOS Version, Device Model, Locale Identifier, Language Code and Country "
                 "Code are device and OS facts the block carries, so they hold one value per image, and First App "
                 "Version is the install's version, one value across an image's blocks except on one image that "
                 "carries two. Last Completed Launch (main app), Last Completed Launch (NSE) and Last Completed "
                 "Launch (share extension) each hold the most recent completed launch of that process as stored, a "
                 "version_build or none or (null), and repeat across an image's blocks when that process did not "
                 "launch again between them. Signal keeps at most three log files per process, each rolled after a "
                 "day or 12 MB, and deletes files older than three days (DebugLogger.swift maximumNumberOfLogFiles "
                 "3, rollingFrequency .day, maximumFileSize 12_000_000, cutoffDate; 3.6.1.4's DebugLogger.m has "
                 "the same three files and daily rolling at 3 MB per file), so this is a recent window and not an "
                 "install history; First App Version is the one field that reaches back to the install.",
        "paths": ('*/Library/Caches/Logs/org.whispersystems.signal *.log',
                  '*/NSELogs/org.whispersystems.signal.SignalNSE *.log',
                  '*/ShareExtensionLogs/org.whispersystems.signal.shareextension *.log'),
        "output_types": "standard",
        "artifact_icon": "power",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | Signal 6.29.0 | 6 rows",
            "adams_iphone12mini": "iOS 17.1.1 | Signal 7_92_1_1315 | 3 rows",
            "dexter_ios18": "iOS 18.3.2 | Signal 7_77_0_1027 | 1 row",
            "falken_ios26": "iOS 26.2.1 | Signal 7_92_1_1315 | 1 row",
            "felix23_ios16": "iOS 16.5 | Signal 6.30.0 | 2 rows",
            "felix_ios17": "iOS 17.6.1 | Signal 7_20_0_218 | 4 rows",
            "fsfull002_ios17": "iOS 17.1 | Signal | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | Signal 7_85_0_1159 | 3 rows",
            "hickman_ios13": "iOS 13.3.1 | Signal 3.6.1 (3_6_1_4) | 4 rows",
            "hickman_ios14": "iOS 14.3 | Signal 5.3.1 (5_3_1_0) | 3 rows",
            "hickman_ios15": "iOS 15.3.1 | Signal 6.22.0 | 2 rows",
            "iphone11_ios17": "iOS 17.3 | Signal 7_21_0_227 | 8 rows",
            "iphone12_ios18": "iOS 18.7 | Signal 7_86_2_1206 | 3 rows",
            "iphone14plus_ios18": "iOS 18.0 | Signal 7_88_0_1238 | 2 rows",
            "jess_ios15": "iOS 15.0.2 | Signal 5.26.10 | 1 row",
            "otto_ios17": "iOS 17.5.1 | Signal 7_23_0_258 | 3 rows",
        },
    },
    "signalLogCallEvents": {
        "name": "Signal - Call Events (logs)",
        "description": "Call signalling events from Signal's debug logs: call messages received and sent with their type "
                       "as stored, call context and status lines and RingRTC events, with the call id and phone number "
                       "tokens as the app logged them.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-05",
        "last_update_date": "2026-09-05",
        "requirements": "none",
        "category": "Signal",
        "notes": "Read from the same logs as the App Launches artifact, with the same UTC handling: Timestamp "
                 "subtracts the log's measured clock offset and Time (as stored) is the line text; Log Clock "
                 "Offset (s) was -14400 on one image's 2020 logs and 0 on the other tested logs. Event names the "
                 "line's origin: a received call message is the MessageReceiver or OWSMessageManager 'handling "
                 "content' line whose content is a CallMessage, with Detail its type as stored (Ice Updates "
                 "<count> on 52 of the 91 received on the tested images, Offer 14, Hangup 12, Answer 11, "
                 "legacyHangup 2); a sent one is the MessageSender line for an OWSOutgoingCallMessage (198); Call "
                 "context is the IndividualCallService line naming the call id and the thread (40); Call status is "
                 "IndividualCallViewController's 'new call status' value (34); RingRTC event is the ringrtc "
                 "library's on_event value (51). Signal scrubs its logs before writing: call ids keep their last "
                 "hex digits as [ REDACTED_HEX:...<digits> ] on 122 events, except on the 2020 and 2021 images, "
                 "whose 9 call ids are unredacted numbers as stored; phone numbers keep their last three digits, "
                 "as [ REDACTED_PHONE_NUMBER:xxx<digits> ] at 6.28.0.11 (the only form on the tested images, on "
                 "the 40 Call context rows) and +x…<digits> from 7.20.0.218 (ScrubbingLogFormatter tests at those "
                 "tags), and release 8.27.0.1843 replaces them with a hash. Call ID and Phone Number are those "
                 "tokens as stored, enough to group the events of one call and not enough to name a party. Process "
                 "names the log source (main app, notification service extension or share extension) and Log File "
                 "is the file each row came from, so both hold one value on an image whose call lines all sit in a "
                 "single main-app log. Of the 23 tested images 4 held call events, 414 in all, and the other 12 "
                 "images with Signal logs held none.",
        "paths": ('*/Library/Caches/Logs/org.whispersystems.signal *.log',
                  '*/NSELogs/org.whispersystems.signal.SignalNSE *.log',
                  '*/ShareExtensionLogs/org.whispersystems.signal.shareextension *.log'),
        "output_types": "standard",
        "artifact_icon": "phone",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | Signal 6.29.0 | 125 rows",
            "adams_iphone12mini": "iOS 17.1.1 | Signal 7_92_1_1315 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | Signal 7_77_0_1027 | 0 rows",
            "falken_ios26": "iOS 26.2.1 | Signal 7_92_1_1315 | 0 rows",
            "felix23_ios16": "iOS 16.5 | Signal 6.30.0 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | Signal 7_20_0_218 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | Signal | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | Signal 7_85_0_1159 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | Signal 3.6.1 (3_6_1_4) | 13 rows",
            "hickman_ios14": "iOS 14.3 | Signal 5.3.1 (5_3_1_0) | 112 rows",
            "hickman_ios15": "iOS 15.3.1 | Signal 6.22.0 | 164 rows",
            "iphone11_ios17": "iOS 17.3 | Signal 7_21_0_227 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | Signal 7_86_2_1206 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | Signal 7_88_0_1238 | 0 rows",
            "jess_ios15": "iOS 15.0.2 | Signal 5.26.10 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | Signal 7_23_0_258 | 0 rows",
        },
    },
}

import os
import re
from datetime import datetime, timedelta, timezone

from scripts.ilapfuncs import artifact_processor, logfunc

_LINE = re.compile(r'^(\d{4}/\d\d/\d\d \d\d:\d\d:\d\d:\d{3})\s+\S+\s+\[([^\]:\s]+)(?::(\d+))?(?:[^\[\]]|\[[^\]]*\])*\]:\s?(.*)$')
_FILE_TIME = re.compile(r' (\d{4}-\d\d-\d\d)--(\d\d)-(\d\d)-(\d\d)-(\d{3})\.log$')
_SOURCE_SUFFIX = re.compile(r'\.(swift|m|rs)$')
_CALL_MESSAGE = re.compile(r'<CallMessage type: ([A-Za-z ]+?)(?: (\d+))?, id: (\[[^\]]*\]|\S+)')
_CALL_CONTEXT = re.compile(r'^callId: (\[[^\]]*\]|\S+), thread: <serviceId: (?:\[[^\]]*\]|\S+), phoneNumber: (\[[^\]]*\]|\S+)>')
_PROCESS = {'Logs': 'Main app', 'NSELogs': 'Notification service extension', 'ShareExtensionLogs': 'Share extension'}
_LAUNCH_FIELDS = (
    ('First App Version', ('firstAppVersion',)),
    ('Last App Version', ('lastAppVersion',)),
    ('Current App Version', ('currentAppReleaseVersion', 'currentAppVersion')),
    ('Current Build', ('currentAppBuildVersion',)),
    ('Last Completed Launch (main app)', ('lastCompletedLaunchMainAppVersion',)),
    ('Last Completed Launch (NSE)', ('lastCompletedLaunchNSEAppVersion',)),
    ('Last Completed Launch (share extension)', ('lastCompletedLaunchSAEAppVersion',)),
    ('iOS Version', ('iOS Version',)),
    ('Device Model', ('Device Model',)),
    ('Locale Identifier', ('Locale Identifier',)),
    ('Country Code', ('Country Code',)),
    ('Language Code', ('Language Code',)),
    ('Build Date/Time (as stored)', ('Build Date/Time',)),
    ('Signal Commit (as stored)', ('Signal Commit',)),
    ('Database Corruption (as stored)', ('Database corruption state',)),
)


def _naive(text):
    try:
        return datetime.strptime(text, '%Y/%m/%d %H:%M:%S:%f')
    except ValueError:
        return None


def _when(text, offset):
    """UTC datetime of a line time: the naive log clock minus the log's measured clock offset."""
    naive = _naive(text)
    if naive is None:
        return ''
    return (naive - timedelta(seconds=offset)).replace(tzinfo=timezone.utc)


def _clock_offset(path, lines):
    """Seconds the log's clock runs ahead of UTC, from its first timestamped line against the UTC
    creation time in the file name (CocoaLumberjack writes the name in UTC in every release the
    tested images used, the lines in UTC only from 3.7.0). Zero within a minute; else rounded to a
    quarter hour."""
    match = _FILE_TIME.search(os.path.basename(path))
    if not match:
        return 0
    created = datetime(int(match.group(1)[:4]), int(match.group(1)[5:7]), int(match.group(1)[8:10]),
                       int(match.group(2)), int(match.group(3)), int(match.group(4)))
    for line in lines:
        head = _LINE.match(line)
        if head:
            first = _naive(head.group(1))
            if first is None:
                return 0
            seconds = (first - created).total_seconds()
            return 0 if abs(seconds) < 60 else int(round(seconds / 900.0) * 900)
    return 0


def _process(path):
    return _PROCESS.get(os.path.basename(os.path.dirname(path)), os.path.basename(os.path.dirname(path)))


def _log_lines(context):
    """(path, time text, source, message, clock offset) for every timestamped line of every Signal log found."""
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if os.path.isdir(file_found) or not file_found.endswith('.log'):
            continue
        try:
            with open(file_found, encoding='utf-8', errors='replace') as handle:
                lines = handle.readlines()
        except OSError as error:
            logfunc(f'Signal log {context.get_relative_path(file_found)} could not be read: {error}')
            continue
        offset = _clock_offset(file_found, lines)
        for line in lines:
            match = _LINE.match(line)
            if not match:
                continue
            source = _SOURCE_SUFFIX.sub('', match.group(2))
            yield file_found, match.group(1), source, match.group(4).rstrip(), offset


@artifact_processor
def signalLogLaunches(context):
    data_headers = (('Launch Time', 'datetime'), 'Launch Time (as stored)', 'Log Clock Offset (s)', 'Process') + tuple(name for name, _keys in _LAUNCH_FIELDS) + ('Log File',)
    data_list = []
    sources = []
    current = {}

    def flush(block):
        if not block:
            return
        fields = block['fields']
        data_list.append((_when(block['time'], block['offset']), block['time'], block['offset'], _process(block['path'])) + tuple(
            next((fields[key] for key in keys if key in fields), '') for _name, keys in _LAUNCH_FIELDS
        ) + (context.get_relative_path(block['path']),))

    for path, time, source, message, offset in _log_lines(context):
        if path not in sources:
            sources.append(path)
        if source == 'AppVersion':
            key, sep, value = message.partition(':')
            if not sep:
                continue
            if key == 'firstAppVersion' or not current or current['path'] != path:
                flush(current)
                current = {'path': path, 'time': time, 'offset': offset, 'fields': {}}
            current['fields'].setdefault(key.strip(), value.strip())
        elif current:
            flush(current)
            current = {}
    flush(current)
    return data_headers, data_list, '\n'.join(context.get_relative_path(p) for p in sources)


@artifact_processor
def signalLogCallEvents(context):
    data_headers = (
        ('Timestamp', 'datetime'),
        'Time (as stored)',
        'Log Clock Offset (s)',
        'Event',
        'Detail (as stored)',
        'Call ID (as stored)',
        'Phone Number (as stored)',
        'Source (as stored)',
        'Process',
        'Log File',
    )
    data_list = []
    sources = []
    for path, time, source, message, offset in _log_lines(context):
        if path not in sources:
            sources.append(path)
        event = detail = call_id = phone = ''
        if source in ('MessageReceiver', 'OWSMessageManager') and 'CallMessage type:' in message:
            match = _CALL_MESSAGE.search(message)
            if not match:
                continue
            event = 'Call message received'
            detail = match.group(1) + (f' {match.group(2)}' if match.group(2) else '')
            call_id = match.group(3)
        elif source == 'MessageSender' and 'OWSOutgoingCallMessage' in message:
            event = 'Call message sent'
            detail = message.split('OWSOutgoingCallMessage', 1)[1].strip(', ')
        elif source == 'IndividualCallService' and message.startswith('callId:'):
            match = _CALL_CONTEXT.match(message)
            if not match:
                continue
            event = 'Call context'
            call_id, phone = match.group(1), match.group(2)
        elif source == 'IndividualCallViewController' and 'new call status:' in message:
            event = 'Call status'
            detail = message.split('new call status:', 1)[1].strip()
        elif source == 'ios_platform' and message.startswith('on_event():'):
            event = 'RingRTC event'
            detail = message.split(':', 1)[1].strip()
        else:
            continue
        data_list.append((_when(time, offset), time, offset, event, detail, call_id, phone, source, _process(path), context.get_relative_path(path)))
    return data_headers, data_list, '\n'.join(context.get_relative_path(p) for p in sources)
