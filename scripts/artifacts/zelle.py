__artifacts_v2__ = {
    "zelle_risk_sdk_events": {
        "name": "Zelle - Risk SDK Events",
        "description": "Start, request, response, device-state and error entries from the debug log "
                       "(Documents/log1.txt) of the device-risk SDK embedded in the Zelle app "
                       "(com.zellepay.zelle).",
        "author": "@danjethh, Claude",
        "creation_date": "2026-11-06",
        "last_update_date": "2026-11-06",
        "requirements": "none",
        "category": "Zelle",
        "notes": (
            "Reads Documents/log1.txt in a container whose metadata plist names com.zellepay.zelle, or in an "
            "iTunes backup AppDomain folder named com.zellepay.zelle. The file is a text log written by an SDK "
            "whose component names are TwoChkCorePlugin, HttpPlugin and ManagerPlugin. Each entry is a header line "
            "'+++ [M-D-YYYY HH:MM:SS] [LEVEL] [Component]' followed by a message line. Event Time is the "
            "bracketed time read as UTC. That held on both research containers we examined: the first entry of the "
            "log fell within 1 s of first_open_timestamp_ms, a UTC epoch value, in the Firebase measurement plist "
            "of the same container (see Zelle - Firebase Analytics). Two containers are a small basis and it is not "
            "established for other app versions. The month is written first: the first field never exceeded 12 "
            "and the second reached 31 in the logs of both containers, and entries were in ascending time order "
            "in both. One row is reported for each entry that "
            "starts the SDK (Two Core Plugin Start; Application has started successfully), each request the app "
            "passed to the SDK (TwoChkGuiReqMsg name), each server response (message type and status code), each "
            "device-state change, each risk reason, each 'Cleared the credentials' entry, and each entry logged at "
            "ERROR level. Event Type, Event and Status are words from the message, as stored; this module does not "
            "state what a request or a status means to the user or the bank. Reported as stored are also the "
            "message text, which can include values the SDK printed (for example a credential length on a "
            "credential-check request). Not reported, because they were repeated or constant in the logs of the two "
            "research containers "
            "and describe the SDK's connection handling rather than the user: socket and connection-state "
            "entries, 'Found Dlg in transaction map', credential enrolment and availability bit values "
            "(constant in both logs), 'Router core get/set environment' and handler plumbing. They are "
            "counted in Zelle - Risk SDK Log Summary. The log is a rolling file, so earlier entries may have been "
            "overwritten; absence of an entry does not show that nothing happened. "
            "Evidence base: the author's own testing on 2 research containers and on synthetic fixtures. The installed app version is 9.4.1 in both containers. MPAppVersion in Mixpanel.plist read 9.3.2 in one container and 9.2.0 in the other; that is the app version at the time the Mixpanel SDK last wrote the key, so the stores were last written by an older build than the installed one, and nothing in either container shows 9.4.1 itself writing them. What is said here about what was seen rests on those two containers; other app versions are untested."
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
        "description": "One row per Zelle risk-SDK log file: first and last entry time, entry counts by level, "
                       "SDK start count and the server host names the log mentions.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-11-06",
        "last_update_date": "2026-11-06",
        "requirements": "none",
        "category": "Zelle",
        "notes": (
            "Built from the same Documents/log1.txt as Zelle - Risk SDK Events and read the same way (Event Time "
            "rules apply to First Entry and Last Entry). Entries is the number of header lines; the Debug and "
            "Error columns count the levels written in those headers (no other level was seen in the logs of the "
            "two research containers). SDK Starts counts 'Application has started successfully' entries. Servers lists the host "
            "names that follow 'siteId:' or 'send connect request to' in the log, de-duplicated and sorted; they "
            "are the SDK vendor's service names and say nothing about a person. The log is a rolling file, so "
            "First Entry is the oldest entry still present, not the first run of the app. "
            "Evidence base: the author's own testing on 2 research containers and on synthetic fixtures. The installed app version is 9.4.1 in both containers. MPAppVersion in Mixpanel.plist read 9.3.2 in one container and 9.2.0 in the other; that is the app version at the time the Mixpanel SDK last wrote the key, so the stores were last written by an older build than the installed one, and nothing in either container shows 9.4.1 itself writing them. What is said here about what was seen rests on those two containers; other app versions are untested."
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
        "description": "Root-detection, malware-detection, SDK initialisation and error lines from the app's "
                       "Library/Caches/file.log.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-11-06",
        "last_update_date": "2026-11-06",
        "requirements": "none",
        "category": "Zelle",
        "notes": (
            "Reads Library/Caches/file.log in a Zelle container. The file holds the app's console lines, one "
            "per line, as 'YYYY-MM-DD HH:MM:SS.mmm Zelle[pid:thread] message'; PID is the process id, which changes "
            "with each launch of the app, and the process name (Zelle on every line) is not reported. Local Time is written without a "
            "time zone, so this column is text and no UTC value is derived. On both research containers the first "
            "line fell a whole number of hours before first_open_timestamp_ms (UTC) in the Firebase measurement "
            "plist of the same container (see Zelle - Firebase Analytics), which fits device local time but does "
            "not establish it. Check is the reporting method named in the line "
            "(EwsMrdExtension getRootStatus or getMalwareStatus) and Result is the word the app printed after "
            "'root status is' or 'malware status is' (NotRooted and NoMalwareDetected on every line seen). A "
            "Result states what the SDK printed, not that the device was or was not modified; this module has "
            "no source for how the SDK reaches it. Other rows are the SDK initialisation steps, the signature "
            "file version line, the session id the SDK logged when generating device logs, the error lines "
            "printed by the Google and payload-handling code, and the Crashlytics version line. The JSON "
            "blocks that follow some lines (keys, signatures, payloads) are not reported. Keyboard-layout "
            "messages and other lines not named above are not reported. A Message longer than 300 characters is "
            "clipped (one payload-error line seen held several thousand). The file is a small cache file: the "
            "two files held 20 and 70 timestamped lines, so it is not a complete launch history. The "
            "session id after 'sessionId:' was empty on every line seen. "
            "Evidence base: the author's own testing on 2 research containers and on synthetic fixtures. The installed app version is 9.4.1 in both containers. MPAppVersion in Mixpanel.plist read 9.3.2 in one container and 9.2.0 in the other; that is the app version at the time the Mixpanel SDK last wrote the key, so the stores were last written by an older build than the installed one, and nothing in either container shows 9.4.1 itself writing them. What is said here about what was seen rests on those two containers; other app versions are untested."
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
        "last_update_date": "2026-11-06",
        "requirements": "none",
        "category": "Zelle",
        "notes": (
            "One row per key of Library/Preferences/com.zellepay.zelle.plist, Library/Preferences/Mixpanel.plist "
            "(the two archived blobs are expanded: super properties here, timed events in Zelle - Mixpanel Timed "
            "Events) and Library/Application Support/com.crashlytics/CLSUserDefaults.plist. Values are as "
            "stored; byte values are shown as hex, lists as JSON. The meaning of a key is not established unless "
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
            "Evidence base: the author's own testing on 2 research containers and on synthetic fixtures. The installed app version is 9.4.1 in both containers. MPAppVersion in Mixpanel.plist read 9.3.2 in one container and 9.2.0 in the other; that is the app version at the time the Mixpanel SDK last wrote the key, so the stores were last written by an older build than the installed one, and nothing in either container shows 9.4.1 itself writing them. What is said here about what was seen rests on those two containers; other app versions are untested."
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
            "that number read as Unix seconds. That reading is checked, not sourced: in both research "
            "containers all values fall between the first and last entry of the Zelle risk-SDK log in the same "
            "container, whereas read as seconds since 2001 they would be in 2054 and 2055. What it is the "
            "start time of is not established; 'timed events' is the Mixpanel SDK's own term and the entries "
            "spanned 375 and 631 days in the two containers, so they are not one session. Event names are app "
            "defined (for example login or an enrolment step name) and are shown as stored. An event in this "
            "dictionary is not evidence that the user completed the step it names. "
            "Evidence base: the author's own testing on 2 research containers and on synthetic fixtures. The installed app version is 9.4.1 in both containers. MPAppVersion in Mixpanel.plist read 9.3.2 in one container and 9.2.0 in the other; that is the app version at the time the Mixpanel SDK last wrote the key, so the stores were last written by an older build than the installed one, and nothing in either container shows 9.4.1 itself writing them. What is said here about what was seen rests on those two containers; other app versions are untested."
        ),
        "paths": (
            '*/Containers/Data/Application/*/Library/Preferences/Mixpanel.plist',
            '*/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist',
        ),
        "output_types": "standard",
        "artifact_icon": "stopwatch",
    },
    "zelle_firebase_analytics": {
        "name": "Zelle - Firebase Analytics",
        "description": "Event counters, user properties and session values the Firebase analytics SDK kept "
                       "inside the Zelle container.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-11-06",
        "last_update_date": "2026-11-06",
        "requirements": "none",
        "category": "Zelle",
        "notes": (
            "Reads the events and user_attributes tables of Library/Application Support/Google/Measurement/"
            "google-app-measurement.sql and selected keys of com.google.gmp.measurement.plist in the same "
            "folder. Event rows: Name is events.name as stored, Count is lifetime_count and Time is "
            "last_fire_timestamp, a float read as Unix seconds; one row per event name, not per occurrence "
            "(raw_events and queue were empty in both research containers). User Property rows: Name, Value and Origin "
            "as stored, Time is set_timestamp as Unix seconds. Record Type tells which file a row came from (Event and User "
            "Property rows are from the database, Measurement plist rows from the plist), so there is no Source File "
            "column. Measurement plist rows: first_open_timestamp_ms "
            "and last_uploaded_event_millis are read as Unix milliseconds, last_engagement_end, "
            "last_successful_upload and last_failed_upload as Unix seconds (a zero leaves Time blank and the stored value is shown in Value), "
            "session_number, app_version, os_version and app_instance_id as stored. Cross-checks that held in both "
            "research containers: the Time of event '_f' equalled first_open_timestamp_ms to the second; "
            "last_engagement_end equalled the latest event Time; the user property '_fot' was a whole number "
            "of hours in milliseconds and within 30 min after first_open_timestamp_ms; the set_timestamp of "
            "'_sid' equalled the Time of event '_s' and its value was within 0.5 s of it; '_sno' equalled "
            "session_number and the Count of '_s'. The names that start with an underscore are the SDK's "
            "own abbreviations and this module does not expand them; '_f', '_vs', '_ab', '_au', '_s', '_ou' "
            "and '_e' and the app-defined 'click' and 'zelle_screen_view' were seen. Value expansions for "
            "'_fi', '_npa', '_lte' and '_se' are not established. os_version is the value last written by "
            "the SDK, not necessarily the OS now installed. Not covered: the other tables of the "
            "database (empty, or SDK configuration and counters, in the two research containers) and google_experimentation_database.sql. "
            "Evidence base: the author's own testing on 2 research containers and on synthetic fixtures. The installed app version is 9.4.1 in both containers. MPAppVersion in Mixpanel.plist read 9.3.2 in one container and 9.2.0 in the other; that is the app version at the time the Mixpanel SDK last wrote the key, so the stores were last written by an older build than the installed one, and nothing in either container shows 9.4.1 itself writing them. What is said here about what was seen rests on those two containers; other app versions are untested."
        ),
        "paths": (
            '*/Containers/Data/Application/*/Library/Application Support/Google/Measurement/google-app-measurement.sql*',
            '*/Containers/Data/Application/*/Library/Application Support/Google/Measurement/com.google.gmp.measurement.plist',
            '*/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist',
        ),
        "output_types": "standard",
        "artifact_icon": "chart-line",
    },
}

import datetime
import json
import os
import plistlib
import re
from xml.parsers.expat import ExpatError

from scripts.ilapfuncs import (artifact_processor, does_table_exist_in_db, get_plist_content,
                               get_sqlite_db_records, logfunc)

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

_MEASUREMENT_PREFIX = '/google/measurement/'
# (key, kind): kind is how the value is read.
_MEASUREMENT_KEYS = (
    ('first_open_timestamp_ms', 'ms'), ('last_uploaded_event_millis', 'ms'),
    ('last_engagement_end', 's'), ('last_successful_upload', 's'), ('last_failed_upload', 's'),
    ('session_number', 'n'), ('app_version', 'text'), ('os_version', 'text'), ('app_instance_id', 'text'),
)


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


def _epoch(value, unit='auto'):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value == 0 or value != value:
        return ''
    if unit == 'auto':
        unit = 'ms' if abs(value) >= 100_000_000_000 else 's'
    try:
        return datetime.datetime.fromtimestamp(value / (1000 if unit == 'ms' else 1), _UTC)
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
    """Yield (time, level, component, message) for each header in a risk-SDK log."""
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
        return 'SDK start', 'Two Core Plugin Start', ''
    if re.match(r'Application\s+has started successfully', message):
        return 'SDK start', 'Application has started successfully', ''
    match = _GUI_REQ_RX.search(message)
    if match and 'GuiRe' in message:
        return 'Request to SDK', match.group(1), ''
    match = _RESPONSE_RX.search(message)
    if match:
        return 'Server response', match.group(1), match.group(2)
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
               ('Debug Entries', 'number'), ('Error Entries', 'number'), ('SDK Starts', 'number'),
               'Servers')
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
    data_headers = ('Local Time', ('PID', 'number'), 'Check', 'Result', 'Message')
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
        return f'SDK step {match.group(1)}', match.group(2)
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
                rows.append((_epoch(started, 's'), str(event)))
    rows.sort(key=lambda r: (r[0] == '', r[0] or datetime.datetime.min.replace(tzinfo=_UTC), r[1]))
    return data_headers, rows, '\n'.join(sources)


@artifact_processor
def zelle_firebase_analytics(context):
    data_headers = (('Time', 'datetime'), 'Record Type', 'Name', 'Value', ('Count', 'number'), 'Origin')
    rows = []
    sources = []
    for path in _zelle_files(context, lambda p: p.endswith(
            ('/Measurement/google-app-measurement.sql', '/Measurement/com.google.gmp.measurement.plist'))):
        display = context.get_relative_path(path)
        sources.append(path)
        if path.endswith('.sql'):
            rows.extend(_firebase_db_rows(os.path.abspath(path), display))
        else:
            plist = _load_plist(path)
            for key, kind in _MEASUREMENT_KEYS:
                if _MEASUREMENT_PREFIX + key not in plist:
                    continue
                value = plist[_MEASUREMENT_PREFIX + key]
                if kind in ('ms', 's'):
                    rows.append((_epoch(value, kind), 'Measurement plist', key,
                                 value if _epoch(value, kind) == '' else '', '', ''))
                else:
                    rows.append(('', 'Measurement plist', key, _show(value), '', ''))
    return data_headers, rows, '\n'.join(sources)


def _firebase_db_rows(path, display):
    rows = []
    if does_table_exist_in_db(path, 'events'):
        for name, count, last_fire in get_sqlite_db_records(
                path, 'SELECT name, lifetime_count, last_fire_timestamp FROM events ORDER BY name'):
            rows.append((_epoch(last_fire), 'Event', name, '', count, ''))
    else:
        logfunc(f'Zelle: no events table; file={display}')
    if does_table_exist_in_db(path, 'user_attributes'):
        for name, stamp, value, origin in get_sqlite_db_records(
                path, 'SELECT name, set_timestamp, value, origin FROM user_attributes ORDER BY name'):
            rows.append((_epoch(stamp), 'User Property', name, _show(value), '', origin))
    else:
        logfunc(f'Zelle: no user_attributes table; file={display}')
    return rows
