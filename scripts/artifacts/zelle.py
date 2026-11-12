__artifacts_v2__ = {
    "zelle_risk_sdk_events": {
        "name": "Zelle - Risk SDK Events",
        "description": "Start, GuiReq, received-message, device-state, risk-reason and error entries from "
                       "Documents/log1.txt, a text log in the Zelle container (com.zellepay.zelle) whose "
                       "component names are TwoChkCorePlugin, HttpPlugin and ManagerPlugin.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-11-06",
        "last_update_date": "2026-11-12",
        "requirements": "none",
        "category": "Zelle",
        "notes": (
            "Risk SDK in the artifact name is a label this module assigns. It is not read from the log. "
            "Reads Documents/log1.txt in a container whose metadata plist names com.zellepay.zelle, or in an "
            "iTunes backup AppDomain folder named com.zellepay.zelle. The file is a text log whose "
            "component names are TwoChkCorePlugin, HttpPlugin and ManagerPlugin. Each entry is a header line "
            "'+++ [M-D-YYYY HH:MM:SS] [LEVEL] [Component]' followed by a message line. Event Time is the "
            "bracketed time read as UTC. That held on both research containers we examined: the first entry of the "
            "log fell within 1 s of first_open_timestamp_ms, a UTC epoch value, in com.google.gmp.measurement.plist "
            "of the same container (read for any app by the Google Measurement - App Analytics Store artifact). "
            "Two containers are a small basis and it is not "
            "established for other app versions. The month is written first: the first field never exceeded 12 "
            "and the second reached 31 in the logs of both containers, and entries were in ascending time order "
            "in both. An entry gives at most one row, and the first rule that matches decides it: a message "
            "'Two Core Plugin Start' (Event Type 'Plugin start'); 'Application has started successfully' (Event Type "
            "'Started successfully'); a message that contains 'GuiRe' and 'received: <word>: <NAME>', where NAME is in capitals (Event Type 'GuiReq received', "
            "Event is NAME); a 'Received msg of type <TYPE>, status code = <CODE>' line (Event Type 'Received msg', "
            "Event is TYPE, Status is CODE); a 'device state set to: <STATE>' line (Event Type 'Device state', Event "
            "is STATE); a 'riskReason' line (Event Type 'Risk reason', Event is the word after riskReason); a "
            "'Cleared the credentials' message (Event Type 'Credentials'); and any other entry logged at ERROR level "
            "(Event Type 'Error'). Event Type is a label this module assigns from the message wording. Event and "
            "Status are words taken from the message, except that Event on the 'Plugin start', 'Started "
            "successfully' and 'Credentials' rows is a fixed phrase the module writes; for an Error entry, Event "
            "is the text before the first comma, at most 80 characters. An entry with an invalid time is treated the same way; its row has an empty Event Time. This module does not state what a GuiReq, a "
            "received message or a status means. Log Message joins the message's body lines with ' / ' and is "
            "clipped at 300 characters; it can include values printed in the message (for example a credential "
            "length on a credential-check request). Not reported, because they were repeated or constant in the "
            "logs of the two research containers: socket and connection-state "
            "entries, 'Found Dlg in transaction map', credential enrolment and availability bit values "
            "(constant in both logs), 'Router core get/set environment' and handler plumbing, unless the entry "
            "is logged at ERROR level. They are "
            "counted in Zelle - Risk SDK Log Summary. Whether the file is rotated or truncated is not "
            "established; absence of an entry does not show that nothing happened. "
            "Evidence base: the author's own testing on 2 research containers and on synthetic fixtures. The installed app version is 9.4.1 in both containers. MPAppVersion in Mixpanel.plist read 9.3.2 in one container and 9.2.0 in the other; that is the app version at the time the Mixpanel SDK last wrote the key. So the installed 9.4.1 build did not update that key. Whether 9.4.1 wrote any of the stores read here is not established. What is said here about what was seen rests on those two containers; other app versions are untested."
        ),
        "paths": (
            '*/Containers/Data/Application/*/Documents/log1.txt',
            '*/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist',
        ),
        "output_types": "standard",
        "artifact_icon": "shield-check",
    },
    "zelle_risk_sdk_log_summary": {
        "name": "Zelle - Risk SDK Log Summary",
        "description": "One row per Documents/log1.txt in a Zelle container: first and last entry time, entry "
                       "counts by level, the count of 'Application has started successfully' entries and the host "
                       "names that follow 'siteId:' or 'send connect request to'.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-11-06",
        "last_update_date": "2026-11-12",
        "requirements": "none",
        "category": "Zelle",
        "notes": (
            "Risk SDK in the artifact name is a label this module assigns. It is not read from the log. "
            "Built from the same Documents/log1.txt as Zelle - Risk SDK Events and read the same way (Event Time "
            "rules apply to First Entry and Last Entry). First Entry and Last Entry are the earliest and latest valid "
            "entry times in the file, not necessarily the first and last entry in it; an entry with an invalid time "
            "is counted in Entries but not used for them. Entries is the number of header lines; the Debug and "
            "Error columns count the levels written in those headers (no other level was seen in the logs of the "
            "two research containers). Start Entries counts 'Application has started successfully' entries. Hosts "
            "lists the host names that follow 'siteId:' or 'send connect request to' in the log, lower-cased, "
            "de-duplicated and sorted; they are names written in the log and say nothing about a person. Whether "
            "the file is rotated or truncated is not established, so the earliest entry in the file may not be the "
            "first run of the app. "
            "Evidence base: the author's own testing on 2 research containers and on synthetic fixtures. The installed app version is 9.4.1 in both containers. MPAppVersion in Mixpanel.plist read 9.3.2 in one container and 9.2.0 in the other; that is the app version at the time the Mixpanel SDK last wrote the key. So the installed 9.4.1 build did not update that key. Whether 9.4.1 wrote any of the stores read here is not established. What is said here about what was seen rests on those two containers; other app versions are untested."
        ),
        "paths": (
            '*/Containers/Data/Application/*/Documents/log1.txt',
            '*/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist',
        ),
        "output_types": "standard",
        "artifact_icon": "list-details",
    },
    "zelle_device_integrity": {
        "name": "Zelle - Device Integrity Checks",
        "description": "Root status, malware status, 'STEP n ---', 'InAuth Sig files versions' and error lines "
                       "from the app's Library/Caches/file.log.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-11-06",
        "last_update_date": "2026-11-12",
        "requirements": "none",
        "category": "Zelle",
        "notes": (
            "Reads Library/Caches/file.log in a Zelle container. The file holds the app's console lines, one "
            "per line, as 'YYYY-MM-DD HH:MM:SS.mmm Zelle[pid:thread] message'; PID is the number before the colon in "
            "the brackets. The process name (Zelle on every line seen) is not reported. Log Time is written without a "
            "time zone, so this column is text and no UTC value is derived. On both research containers the first "
            "line fell a whole number of hours before first_open_timestamp_ms (UTC) in com.google.gmp.measurement.plist "
            "of the same container (read for any app by the Google Measurement - App Analytics Store "
            "artifact), which fits device local time but does "
            "not establish it. Check is a label this module assigns from the line's wording; for the two status lines it comes from "
            "the method named in the line (getRootStatus or getMalwareStatus). An entry gives at most one row, and "
            "the first rule that matches decides it. Result is the word the app printed after 'root status is' or "
            "'malware status is' on the two status lines only (NotRooted and NoMalwareDetected on every line seen); "
            "it is the word printed, not a finding that the device was or was not modified, and this module has no "
            "source for how the status is reached. Other rows are the 'running root detection' and 'running "
            "malware detection' lines (Result 'started', a fixed word the module writes), the 'Root scan list not "
            "found' line (Result 'not found', also fixed), the 'STEP n ---' lines (Check 'STEP n', Result the text "
            "after the dashes without trailing dots), the signature file version line (Result the text after "
            "'versions: '), the session id on the 'Generating device logs for sessionId:' line (Result the session "
            "id), the Crashlytics version line (Result the last word of the message), and lines that contain ERROR or "
            "start with Error (Result the first 80 characters of the message). "
            "Untimestamped lines, "
            "such as the JSON blocks that follow some lines (keys, signatures, payloads), are not reported; JSON "
            "on a timestamped line itself is part of its Message and is clipped with it. Keyboard-layout "
            "messages and other lines not named above are not reported. A Message longer than 300 characters is "
            "clipped (one payload-error line seen held several thousand). The "
            "two files held 20 and 70 timestamped lines. Whether the file keeps every launch is not established. The "
            "session id after 'sessionId:' was empty on every line seen. "
            "Evidence base: the author's own testing on 2 research containers and on synthetic fixtures. The installed app version is 9.4.1 in both containers. MPAppVersion in Mixpanel.plist read 9.3.2 in one container and 9.2.0 in the other; that is the app version at the time the Mixpanel SDK last wrote the key. So the installed 9.4.1 build did not update that key. Whether 9.4.1 wrote any of the stores read here is not established. What is said here about what was seen rests on those two containers; other app versions are untested."
        ),
        "paths": (
            '*/Containers/Data/Application/*/Library/Caches/file.log',
            '*/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "device-mobile-check",
    },
    "zelle_preferences": {
        "name": "Zelle - Preferences and Identifiers",
        "description": "Keys and values of the Zelle app's preference plist, its Mixpanel plist (including the "
                       "archived super properties) and its Crashlytics defaults.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-11-06",
        "last_update_date": "2026-11-12",
        "requirements": "none",
        "category": "Zelle",
        "notes": (
            "One row per key of Library/Preferences/com.zellepay.zelle.plist, Library/Preferences/Mixpanel.plist "
            "(the two archived blobs are expanded: super properties here, timed events in Zelle - Mixpanel Timed "
            "Events) and Library/Application Support/com.crashlytics/CLSUserDefaults.plist. Value shows bytes as hex "
            "(bytes longer than 64 are cut to the first 64 bytes of hex, followed by '...'), lists and dicts as "
            "JSON with sorted keys, in which bytes are shown as full hex, and dates as ISO text; other values are "
            "shown as stored. The super properties are shown as decoded from the archive; a super properties value that cannot be decoded gives no row. Value Type is the "
            "Python type name of the value. The meaning of a key is not established unless "
            "the key's own name states it. Keys seen in the two research containers were: AccountAssociatedWithUserKey, "
            "AppAlreadyLaunchedKey, PreferencesTouchIDKey, PushIDKey (32 bytes), qrCodeSeen, zrcSeen, "
            "ShouldKeepPrivacySettingsKey, trackedKey, MixpanelRecordEventType (DONT_RECORD in one container, "
            "RECORD in the other), SafeUserAlertWhitelist and RecipientNameAlertWhitelist (both empty lists in "
            "both containers, so what an entry looks like is not established), SKPurchaseIntentUpdatesLastChecked "
            "(one container only, a float whose epoch is not established). Mixpanel.plist carried MPAppVersion "
            "(9.3.2 and 9.2.0 in the two containers) and identifier strings named MPUserId, MPDistinctID, "
            "MPPeopleDistinctID and MPAnonymousId. Those are identifiers an examiner can take to the service "
            "provider; this module does not state whose they are. The super properties in the two containers "
            "were app-state flags and screen names ('Current App Screen' on both, 'Last App Screen' in one); each is the value at the time the plist was last written, not a history. A missing key is "
            "not evidence that a setting is off. The Mixpanel event queue (AppStore_MPDB.sqlite) is covered by "
            "the Mixpanel - Events artifact, and the app plist is also listed by the generic Application User "
            "Defaults artifact. "
            "Evidence base: the author's own testing on 2 research containers and on synthetic fixtures. The installed app version is 9.4.1 in both containers. MPAppVersion in Mixpanel.plist read 9.3.2 in one container and 9.2.0 in the other; that is the app version at the time the Mixpanel SDK last wrote the key. So the installed 9.4.1 build did not update that key. Whether 9.4.1 wrote any of the stores read here is not established. What is said here about what was seen rests on those two containers; other app versions are untested."
        ),
        "paths": (
            '*/Containers/Data/Application/*/Library/Preferences/com.zellepay.zelle.plist',
            '*/Containers/Data/Application/*/Library/Preferences/Mixpanel.plist',
            '*/Containers/Data/Application/*/Library/Application Support/com.crashlytics/CLSUserDefaults.plist',
            '*/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "settings",
    },
    "zelle_mixpanel_timed_events": {
        "name": "Zelle - Mixpanel Timed Events",
        "description": "Event names and start times held in the archived timedEvents dictionary of the Zelle "
                       "Mixpanel plist.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-11-06",
        "last_update_date": "2026-11-06",
        "requirements": "none",
        "category": "Zelle",
        "notes": (
            "Reads the mixpanel-<name>-timedEvents key of Library/Preferences/Mixpanel.plist, an "
            "NSKeyedArchiver NSDictionary of event name to a number, with the core's plist helper. Start Time is "
            "that number read as Unix seconds. Sources: mixpanel-swift at commit "
            "38e63de7d71a2b6787bbd190ef8fcc04d053f259 (MixpanelInstance.swift, time(event:)) takes "
            "Date().timeIntervalSince1970 when the app calls time(event:), and mixpanel-iphone at commit "
            "1e0a3c5a59b018507555d52ae60246c4237b0ef0 (Mixpanel.m, timeEvent:) does the same. "
            "Consistent with that, in both research containers all values fall between the first and last "
            "entry of Documents/log1.txt in the same container, whereas read as seconds since 2001 they would "
            "be in 2054 and 2055. What the value is the start time of in a given container is not established "
            "beyond those sources; the key is named timedEvents and the entries "
            "spanned 375 and 631 days in the two containers, so they are not one session. Event names are app "
            "defined (for example login or an enrolment step name) and are shown as stored. An event in this "
            "dictionary is not evidence that the user completed the step it names. "
            "Evidence base: the author's own testing on 2 research containers and on synthetic fixtures. The installed app version is 9.4.1 in both containers. MPAppVersion in Mixpanel.plist read 9.3.2 in one container and 9.2.0 in the other; that is the app version at the time the Mixpanel SDK last wrote the key. So the installed 9.4.1 build did not update that key. Whether 9.4.1 wrote any of the stores read here is not established. What is said here about what was seen rests on those two containers; other app versions are untested."
        ),
        "paths": (
            '*/Containers/Data/Application/*/Library/Preferences/Mixpanel.plist',
            '*/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist',
        ),
        "output_types": "standard",
        "artifact_icon": "stopwatch",
    },
}

import datetime
import json
import os
import plistlib
import re
from xml.parsers.expat import ExpatError

from scripts.ilapfuncs import artifact_processor, get_plist_content, logfunc

_BUNDLE = 'com.zellepay.zelle'
_METADATA = '.com.apple.mobile_container_manager.metadata.plist'
_CONTAINER_RX = re.compile(r'^(.*?/Containers/Data/Application/([^/]+))/', re.I)
_UTC = datetime.timezone.utc

_ENTRY_RX = re.compile(r'^\+\+\+ \[(\d{1,2})-(\d{1,2})-(\d{4}) (\d{1,2}):(\d{2}):(\d{2})\] \[(\w+)\] \[([^\]]*)\]')
_CONSOLE_RX = re.compile(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(?:\.\d+)?) (\S+?)\[(\d+):(\w+)\] (.*)$')
_GUI_REQ_RX = re.compile(r'received: \w+: ([A-Z][A-Z0-9_]+)')
_RESPONSE_RX = re.compile(r'Received msg of type (\w+), status code =\s*(\w*)')
_DEVICE_STATE_RX = re.compile(r'device state set to: (\w+)')
_RISK_REASON_RX = re.compile(r'riskReason\s+(\w+)')
_HOST_RX = re.compile(r'(?:siteId:|send connect request to )\s*([A-Za-z0-9][A-Za-z0-9.-]*\.[A-Za-z]{2,})')
_ROOT_RX = re.compile(r'getRootStatus:+ root status is: (\S+)')
_MALWARE_RX = re.compile(r'getMalwareStatus:+ malware status is: (\S+)')
_STEP_RX = re.compile(r'^STEP (\d+) --- (.*?)\.*$')
_SIG_RX = re.compile(r'InAuth Sig files versions: (.*)')
_SESSION_RX = re.compile(r'Generating device logs for sessionId: (\S*)')


def _norm(path):
    return str(path).replace('\\', '/')


def _container_bundles(files):
    """Map container prefix to the bundle id in its metadata plist."""
    bundles = {}
    for path in files:
        norm = _norm(path)
        if not norm.endswith('/' + _METADATA):
            continue
        match = _CONTAINER_RX.match(norm)
        if not match or norm.rsplit('/', 1)[0] != match.group(1):
            continue
        try:
            with open(path, 'rb') as handle:
                data = plistlib.load(handle)
        except (OSError, ValueError, TypeError, OverflowError, ExpatError, plistlib.InvalidFileException):
            logfunc(f'Zelle: unreadable container metadata; file={os.path.basename(os.path.dirname(path))}')
            continue
        identifier = data.get('MCMMetadataIdentifier') if isinstance(data, dict) else None
        if isinstance(identifier, str):
            bundles[match.group(1)] = identifier
    return bundles


def _zelle_files(context, name_matches):
    """Found files whose name satisfies name_matches and that sit in a Zelle container.

    A container qualifies when its metadata plist names the bundle, or when its folder is named by the
    bundle id, which is how an iTunes backup names an AppDomain.
    """
    files = sorted({str(p) for p in context.get_files_found()})
    bundles = _container_bundles(files)
    found = []
    for path in files:
        norm = _norm(path)
        if not name_matches(norm):
            continue
        match = _CONTAINER_RX.match(norm)
        if match and (match.group(2) == _BUNDLE or bundles.get(match.group(1)) == _BUNDLE):
            found.append(path)
    return found


def _utc(year, month, day, hour, minute, second):
    try:
        return datetime.datetime(year, month, day, hour, minute, second, tzinfo=_UTC)
    except ValueError:
        return ''


def _epoch(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value == 0 or value != value:
        return ''
    try:
        return datetime.datetime.fromtimestamp(value, _UTC)
    except (ValueError, OverflowError, OSError):
        return ''


def _show(value):
    if isinstance(value, bytes):
        return value.hex() if len(value) <= 64 else value[:64].hex() + '...'
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True, default=_json_default)
    if isinstance(value, (datetime.datetime, datetime.date)):
        return value.isoformat()
    return value


def _json_default(value):
    if isinstance(value, bytes):
        return value.hex()
    return str(value)


def _clip(text, limit=300):
    return text if len(text) <= limit else text[:limit] + '...'


def _read_lines(path):
    try:
        with open(path, 'r', encoding='utf-8', errors='replace') as handle:
            return handle.read().splitlines()
    except OSError:
        logfunc(f'Zelle: could not read {os.path.basename(path)}')
        return []


def _sdk_entries(path):
    """Yield (time, level, component, message) for each header in a Documents/log1.txt log."""
    header = None
    body = []

    def flush():
        if header is None:
            return None
        return header + (' / '.join(body),)

    for line in _read_lines(path):
        match = _ENTRY_RX.match(line)
        if match:
            done = flush()
            if done:
                yield done
            month, day, year, hour, minute, second = (int(match.group(i)) for i in range(1, 7))
            header = (_utc(year, month, day, hour, minute, second), match.group(7), match.group(8))
            body = []
        elif header is not None and line.strip():
            body.append(line.strip())
    done = flush()
    if done:
        yield done


def _classify(level, message):
    """Return (event type, event, status) for a message worth reporting, else None."""
    if message.startswith('Two Core Plugin Start'):
        return 'Plugin start', 'Two Core Plugin Start', ''
    if re.match(r'Application\s+has started successfully', message):
        return 'Started successfully', 'Application has started successfully', ''
    match = _GUI_REQ_RX.search(message)
    if match and 'GuiRe' in message:
        return 'GuiReq received', match.group(1), ''
    match = _RESPONSE_RX.search(message)
    if match:
        return 'Received msg', match.group(1), match.group(2)
    match = _DEVICE_STATE_RX.search(message)
    if match:
        return 'Device state', match.group(1), ''
    match = _RISK_REASON_RX.search(message)
    if match:
        return 'Risk reason', match.group(1), ''
    if message.startswith('Cleared the credentials'):
        return 'Credentials', 'Cleared the credentials', ''
    if level.upper() == 'ERROR':
        return 'Error', message.split(',')[0][:80], ''
    return None


@artifact_processor
def zelle_risk_sdk_events(context):
    data_headers = (('Event Time', 'datetime'), 'Level', 'Component', 'Event Type', 'Event', 'Status',
               'Log Message')
    rows = []
    sources = []
    for path in _zelle_files(context, lambda p: p.endswith('/Documents/log1.txt')):
        display = context.get_relative_path(path)
        sources.append(path)
        for stamp, level, component, message in _sdk_entries(path):
            if stamp == '':
                logfunc(f'Zelle: entry with an invalid time skipped for the timeline; file={display}')
            kind = _classify(level, message)
            if kind is None:
                continue
            rows.append((stamp, level, component, kind[0], kind[1], kind[2], _clip(message)))
    return data_headers, rows, '\n'.join(sources)


@artifact_processor
def zelle_risk_sdk_log_summary(context):
    data_headers = (('First Entry', 'datetime'), ('Last Entry', 'datetime'), ('Entries', 'number'),
               ('Debug Entries', 'number'), ('Error Entries', 'number'), ('Start Entries', 'number'),
               'Hosts')
    rows = []
    sources = []
    for path in _zelle_files(context, lambda p: p.endswith('/Documents/log1.txt')):
        sources.append(path)
        stamps = []
        total = debug = errors = starts = 0
        hosts = set()
        for stamp, level, _component, message in _sdk_entries(path):
            total += 1
            debug += level.upper() == 'DEBUG'
            errors += level.upper() == 'ERROR'
            if re.match(r'Application\s+has started successfully', message):
                starts += 1
            if stamp != '':
                stamps.append(stamp)
            hosts.update(h.lower() for h in _HOST_RX.findall(message))
        if total:
            rows.append((min(stamps) if stamps else '', max(stamps) if stamps else '', total, debug, errors,
                         starts, '; '.join(sorted(hosts))))
    return data_headers, rows, '\n'.join(sources)


@artifact_processor
def zelle_device_integrity(context):
    data_headers = ('Log Time', ('PID', 'number'), 'Check', 'Result', 'Message')
    rows = []
    sources = []
    for path in _zelle_files(context, lambda p: p.endswith('/Library/Caches/file.log')):
        sources.append(path)
        for line in _read_lines(path):
            match = _CONSOLE_RX.match(line)
            if not match:
                continue
            stamp, _process, pid, _thread, message = match.groups()
            check, result = _integrity_line(message)
            if check is None:
                continue
            rows.append((stamp, int(pid), check, result, _clip(message)))
    return data_headers, rows, '\n'.join(sources)


def _integrity_line(message):
    match = _ROOT_RX.search(message)
    if match:
        return 'Root status', match.group(1)
    match = _MALWARE_RX.search(message)
    if match:
        return 'Malware status', match.group(1)
    if 'running root detection' in message:
        return 'Root detection', 'started'
    if 'running malware detection' in message:
        return 'Malware detection', 'started'
    if message.startswith('Root scan list not found'):
        return 'Root scan list', 'not found'
    match = _SIG_RX.search(message)
    if match:
        return 'Signature files version', match.group(1)
    match = _STEP_RX.match(message)
    if match:
        return f'STEP {match.group(1)}', match.group(2)
    match = _SESSION_RX.search(message)
    if match:
        return 'Device log generation', match.group(1)
    if message.startswith('[Firebase/Crashlytics] Version'):
        return 'Crashlytics', message.rsplit(' ', 1)[-1]
    if 'ERROR' in message or message.startswith('Error'):
        return 'Error', message[:80]
    return None, None


def _load_plist(path):
    try:
        with open(path, 'rb') as handle:
            data = plistlib.load(handle)
    except (OSError, ValueError, TypeError, OverflowError, ExpatError, plistlib.InvalidFileException):
        logfunc(f'Zelle: unreadable plist; file={os.path.basename(path)}')
        return {}
    return data if isinstance(data, dict) else {}


def _archived_dict(blob):
    """Decode an NSKeyedArchiver dictionary stored as bytes in a plist; {} if it is not one."""
    if not isinstance(blob, bytes):
        return {}
    decoded = get_plist_content(blob)
    return decoded if isinstance(decoded, dict) else {}


def _is_blob_key(key, suffix):
    return key.startswith('mixpanel-') and key.endswith(suffix)


@artifact_processor
def zelle_preferences(context):
    data_headers = ('Preference File', 'Key', 'Value', 'Value Type')
    rows = []
    sources = []
    wanted = ('/Library/Preferences/com.zellepay.zelle.plist', '/Library/Preferences/Mixpanel.plist',
              '/com.crashlytics/CLSUserDefaults.plist')
    for path in _zelle_files(context, lambda p: p.endswith(wanted)):
        sources.append(path)
        name = os.path.basename(path)
        for key, value in sorted(_load_plist(path).items()):
            if name == 'Mixpanel.plist' and _is_blob_key(key, '-timedEvents'):
                continue
            if name == 'Mixpanel.plist' and _is_blob_key(key, '-superProperties'):
                for prop, prop_value in sorted(_archived_dict(value).items(), key=lambda kv: str(kv[0])):
                    rows.append((f'{name} (superProperties)', str(prop), _show(prop_value),
                                 type(prop_value).__name__))
                continue
            rows.append((name, key, _show(value), type(value).__name__))
    return data_headers, rows, '\n'.join(sources)


@artifact_processor
def zelle_mixpanel_timed_events(context):
    data_headers = (('Start Time', 'datetime'), 'Event Name')
    rows = []
    sources = []
    for path in _zelle_files(context, lambda p: p.endswith('/Library/Preferences/Mixpanel.plist')):
        sources.append(path)
        for key, value in _load_plist(path).items():
            if not _is_blob_key(key, '-timedEvents'):
                continue
            for event, started in sorted(_archived_dict(value).items(), key=lambda kv: str(kv[0])):
                rows.append((_epoch(started), str(event)))
    rows.sort(key=lambda r: (r[0] == '', r[0] or datetime.datetime.min.replace(tzinfo=_UTC), r[1]))
    return data_headers, rows, '\n'.join(sources)
