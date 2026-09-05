__artifacts_v2__ = {
    "ips_reports": {
        "name": "iOS Diagnostic Reports - Index",
        "description": "One row for each .ips diagnostic report in the CrashReporter folders, with the time the "
                       "report was written, its kind, the process or app it names, and the OS build.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-05",
        "last_update_date": "2026-09-05",
        "requirements": "none",
        "category": "iOS Diagnostic Reports",
        "notes": "Read from the .ips files under Library/Logs/CrashReporter and its Retired "
                 "subfolder. Every .ips file opens with one line of JSON metadata; the rest of "
                 "the file is the report body, which is JSON for some kinds and text for others. "
                 "Reference: Apple, 'Interpreting the JSON format of a crash report', "
                 "https://developer.apple.com/documentation/xcode/interpreting-the-json-format-of-a-crash-report, "
                 "which documents the metadata keys name, bug_type, bundleID, build_version, "
                 "incident_id, platform and timestamp, names 309 as the crash report type and 288 "
                 "as a stackshot, and says other types exist. Report Kind is the file name before "
                 "its date, as stored; the other bug types are reported as stored and are not "
                 "interpreted here. Report Time is the metadata timestamp, which carries a UTC "
                 "offset, rendered in UTC; OS Version is the metadata os_version, one value per "
                 "device. Process or App is the metadata name or app_name, and App Version and "
                 "Build Version are the metadata app_version and build_version, present only on "
                 "reports whose metadata names an app or process; for the app-usage and "
                 "notification-setting kinds, whose metadata carries no name, Bundle ID is filled "
                 "from the body. Retired is True when the file sat in the Retired subfolder. The "
                 "crash, app-usage, resource, jetsam and stackshot kinds are decoded in the "
                 "sibling artifacts; this index lists every report so a kind with no decoder is "
                 "still visible with its time. A file that opens without a metadata line is still "
                 "listed, with its name, size and location only: on three tested images that was "
                 "one rtcreportingd_<date>_messageLog.ips each, a text log of JSON event blocks "
                 "rather than a report. On the tested images the kinds included JetsamEvent, "
                 "SiriSearchFeedback, stacks, WiFiLQMMetrics, xp_amp_app_usage_dnu, "
                 "TransparencyTopic, KeySyncTopic, log-aggregated, LowBatteryLog, ResetCounter, "
                 "the <process>.cpu_resource, .wakeups_resource and .diskwrites_resource reports, "
                 "and reports named after the crashed app.",
        "paths": ('*/Library/Logs/CrashReporter/*.ips',),
        "output_types": "standard",
        "artifact_icon": "file-text",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 161 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 0 rows",
            "belkactf6": "iOS 16.3 | 26 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 31 rows",
            "ctf2020_ios12": "iOS 12.4 | 169 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "falken_ios26": "iOS 26.2.1 | 84 rows",
            "felix23_ios16": "iOS 16.5 | 120 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 20 rows",
            "hc_ios26": "iOS 26.5.2 | 37 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 99 rows",
            "hickman_ios14": "iOS 14.3 | 154 rows",
            "hickman_ios15": "iOS 15.3.1 | 133 rows",
            "iphone11_ios17": "iOS 17.3 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 0 rows",
            "jess_ios15": "iOS 15.0.2 | 51 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
        },
    },
    "ips_app_crashes": {
        "name": "iOS Diagnostic Reports - App and Process Crashes",
        "description": "Crash reports for apps and system processes, with the crash time, the process launch "
                       "time, the process and bundle, its role, the exception and the termination reason.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-05",
        "last_update_date": "2026-09-05",
        "requirements": "none",
        "category": "iOS Diagnostic Reports",
        "notes": "Read from the .ips reports whose metadata bug_type is 309 (JSON body) or 109 "
                 "(text body). The JSON form is documented by Apple in 'Interpreting the JSON "
                 "format of a crash report' "
                 "(https://developer.apple.com/documentation/xcode/interpreting-the-json-format-of-a-crash-report): "
                 "Crash Time is captureTime, Launch Time is procLaunch, Process and PID are "
                 "procName and pid, Bundle ID and Version come from bundleInfo, Role is procRole, "
                 "Parent Process is parentProc with parentPid, Exception Type is the exception "
                 "type with its signal, Termination Reason is the termination namespace and code, "
                 "the code shown in hexadecimal as Apple documents, followed by the indicator "
                 "where present, Hardware Model is modelCode and Time Awake Since Boot (s) is "
                 "uptime, blank for the text form, which has no such line. Exception Note renders "
                 "isCorpse, isNonFatal and isSimulated with the wording Apple gives for the "
                 "translated report: EXC_CORPSE_NOTIFY, NON-FATAL CONDITION (this isn't a crash) "
                 "and SIMULATED (this isn't a crash). Device Locked and Unlocked Since Boot are "
                 "the isLocked and wasUnlockedSinceBoot values of the JSON form as stored; "
                 "Apple's page does not document them, they are blank for the text form, and "
                 "isLocked was present on 4 of the 35 JSON-form reports of the tested images. "
                 "Report Form says which body the row came from: text on the iOS 12, 13 and 14 "
                 "images and JSON on iOS 15 and later, 75 and 35 reports across the tested "
                 "images. The text form carries the same facts as labelled lines: Process, "
                 "Identifier, Version, Role, Parent Process, Date/Time, Launch Time, Exception "
                 "Type, Exception Note, Termination Reason, Termination Description, Hardware "
                 "Model and OS Version, read as stored. Both forms name the process the report "
                 "applies to; a report whose Exception Note says SIMULATED or NON-FATAL is one "
                 "Apple says is not a crash, and the ExcUserFault_<process> reports on the tested "
                 "images are of that kind. Times carry a UTC offset in both forms and are "
                 "rendered in UTC. A crash report records that the process was running at Crash "
                 "Time and had been launched at Launch Time; it does not by itself show who was "
                 "using the device.",
        "paths": ('*/Library/Logs/CrashReporter/*.ips',),
        "output_types": "standard",
        "artifact_icon": "alert-triangle",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 2 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 0 rows",
            "belkactf6": "iOS 16.3 | 2 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 0 rows",
            "ctf2020_ios12": "iOS 12.4 | 60 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "falken_ios26": "iOS 26.2.1 | 2 rows",
            "felix23_ios16": "iOS 16.5 | 3 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "hc_ios26": "iOS 26.5.2 | 0 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 9 rows",
            "hickman_ios14": "iOS 14.3 | 6 rows",
            "hickman_ios15": "iOS 15.3.1 | 26 rows",
            "iphone11_ios17": "iOS 17.3 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 0 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
        },
    },
    "ips_app_usage": {
        "name": "iOS Diagnostic Reports - App Usage Ranges",
        "description": "App install, launch and crash counts and foreground duration per app over "
                       "a time range, from the xp_amp_app_usage_dnu diagnostic reports.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-05",
        "last_update_date": "2026-09-05",
        "requirements": "none",
        "category": "iOS Diagnostic Reports",
        "notes": "Read from the .ips reports whose metadata bug_type is 225, named "
                 "xp_amp_app_usage_dnu on the tested images. The body is a JSON array; each entry "
                 "carries bundleId, eventType, count, rangeStartTime and rangeEndTime in Unix "
                 "seconds, eventTime in Unix milliseconds, foregroundDuration, shortAppVersion, "
                 "storefront and cohort. Apple does not document this report, so the columns "
                 "carry the entry's own key names and values as stored: Count is the count for "
                 "the Event Type over the range, and Foreground Duration is the "
                 "foregroundDuration number with no unit stated. Reporting App is the entry's app "
                 "value, which on every tested entry was com.apple.appstored, the App Store "
                 "daemon. Cohort is the entry's cohort string as stored, an App Store page "
                 "reference on the tested images. Event Type was installs, launches or crashes on "
                 "the tested images (1,589, 144 and 2 of the 1,735 entries on four images). A row "
                 "records that the report counted Count events of that type for the app in the "
                 "range; the range spanned twelve hours on 1,646 entries, four hours on 88 and 21 "
                 "hours on one.",
        "paths": ('*/Library/Logs/CrashReporter/*.ips',),
        "output_types": "standard",
        "artifact_icon": "bar-chart-2",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 776 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 0 rows",
            "belkactf6": "iOS 16.3 | 0 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 0 rows",
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "falken_ios26": "iOS 26.2.1 | 0 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "hc_ios26": "iOS 26.5.2 | 461 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 365 rows",
            "hickman_ios14": "iOS 14.3 | 133 rows",
            "hickman_ios15": "iOS 15.3.1 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 0 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
        },
    },
    "ips_resource_reports": {
        "name": "iOS Diagnostic Reports - Resource Exceptions",
        "description": "Reports of a process exceeding a CPU, wakeup or disk-write limit, with the window the "
                       "process was observed in, the process, the event and the action the system took.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-05",
        "last_update_date": "2026-09-05",
        "requirements": "none",
        "category": "iOS Diagnostic Reports",
        "notes": "Read from the .ips reports named <process>.cpu_resource, .wakeups_resource, "
                 ".diskwrites_resource and .cpu_resource_fatal, whose bodies are text with "
                 "labelled lines. Start and End are the Date/Time and End time lines, which carry "
                 "a UTC offset and are rendered in UTC; Process, PID, Event, Action Taken and "
                 "Duration are the Command, PID, Event, Action taken and Duration lines as "
                 "stored; Detail is the line describing the limit that was exceeded (Wakeups, CPU "
                 "or Writes); Hardware Model and OS Version are the Hardware model and OS Version "
                 "lines, one value per device. Apple does not publish the layout of these "
                 "reports; the labels are read as they appear. A row records that the process was "
                 "running between Start and End.",
        "paths": ('*/Library/Logs/CrashReporter/*.ips',),
        "output_types": "standard",
        "artifact_icon": "activity",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 14 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 0 rows",
            "belkactf6": "iOS 16.3 | 0 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 0 rows",
            "ctf2020_ios12": "iOS 12.4 | 9 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "falken_ios26": "iOS 26.2.1 | 15 rows",
            "felix23_ios16": "iOS 16.5 | 10 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 3 rows",
            "hc_ios26": "iOS 26.5.2 | 2 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 11 rows",
            "hickman_ios14": "iOS 14.3 | 13 rows",
            "hickman_ios15": "iOS 15.3.1 | 38 rows",
            "iphone11_ios17": "iOS 17.3 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 0 rows",
            "jess_ios15": "iOS 15.0.2 | 2 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
        },
    },
    "ips_snapshot_events": {
        "name": "iOS Diagnostic Reports - Jetsam Events and Stackshots",
        "description": "Each jetsam event and stackshot report, with its time, the reason, the process the "
                       "system jettisoned, the largest process and the processes that were frontmost.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-05",
        "last_update_date": "2026-09-05",
        "requirements": "none",
        "category": "iOS Diagnostic Reports",
        "notes": "Read from the .ips reports whose metadata bug_type is 298 (JetsamEvent) or 288 "
                 "(stackshot, named stacks or stacks+<app> on the tested images). Both bodies are "
                 "JSON; Kind says which, and OS Build is the report's build value, one value per "
                 "device. The jetsam report is documented by Apple in 'Identifying high-memory "
                 "use with jetsam event reports' "
                 "(https://developer.apple.com/documentation/xcode/identifying-high-memory-use-with-jetsam-event-reports): "
                 "largestProcess names the process using the most memory pages, only the "
                 "jettisoned process carries a reason, and the documented reasons are "
                 "per-process-limit, vm-pageshortage, vnode-limit, highwater, fc-thrashing and "
                 "jettisoned; the tested images also carried sustained-memory-pressure, "
                 "vm-compressor-space-shortage, vm-compressor-thrashing and (unknown-kill), "
                 "reported as stored; Page Size is memoryStatus.pageSize. Frontmost Processes "
                 "lists the jetsam processes whose states include frontmost, or the stackshot "
                 "processes whose pids are in frontmostPids. The stackshot reason and its process "
                 "list (processByPid) are read as stored; Apple's page names 288 as a stackshot "
                 "and documents nothing more of it. Time is the report's date value, which "
                 "carries a UTC offset, rendered in UTC. Processes Listed is the number of "
                 "process entries in the report. A row records the processes the system saw at "
                 "Time.",
        "paths": ('*/Library/Logs/CrashReporter/*.ips',),
        "output_types": "standard",
        "artifact_icon": "camera",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 60 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 0 rows",
            "belkactf6": "iOS 16.3 | 7 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 6 rows",
            "ctf2020_ios12": "iOS 12.4 | 99 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "falken_ios26": "iOS 26.2.1 | 2 rows",
            "felix23_ios16": "iOS 16.5 | 29 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 4 rows",
            "hc_ios26": "iOS 26.5.2 | 7 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 18 rows",
            "hickman_ios14": "iOS 14.3 | 20 rows",
            "hickman_ios15": "iOS 15.3.1 | 31 rows",
            "iphone11_ios17": "iOS 17.3 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 0 rows",
            "jess_ios15": "iOS 15.0.2 | 3 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
        },
    },
    "ips_snapshot_processes": {
        "name": "iOS Diagnostic Reports - Processes in Jetsam Snapshots",
        "description": "The non-daemon processes listed in each jetsam event report, with the snapshot time, "
                       "the process, its states and its memory pages.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-05",
        "last_update_date": "2026-09-05",
        "requirements": "none",
        "category": "iOS Diagnostic Reports",
        "notes": "Read from the processes array of each bug_type 298 JetsamEvent report. "
                 "Reference: Apple, 'Identifying high-memory use with jetsam event reports', "
                 "https://developer.apple.com/documentation/xcode/identifying-high-memory-use-with-jetsam-event-reports, "
                 "which documents name, pid, states (such as frontmost or suspended), rpages, "
                 "lifetimeMax, coalition, uuid and reason. Entries whose states include daemon "
                 "are left out, because they are system services rather than apps; the count left "
                 "out is written to the log (54,599 of 66,290 entries across the tested images, "
                 "leaving 11,691 rows, 551 of them frontmost). States are joined as stored; "
                 "Frontmost is True when they include frontmost. Resident Pages and Lifetime Max "
                 "Pages are rpages and lifetimeMax in memory pages of the Page Size the parent "
                 "report states. Jetsam Reason is set on the one jettisoned process of each "
                 "report and blank on the rest. Age is the entry's age value as stored, with no "
                 "unit stated. Snapshot Time is the report's date, rendered in UTC. A row records "
                 "that the process existed at Snapshot Time in the state shown; suspended and "
                 "idle processes were resident but not necessarily in use.",
        "paths": ('*/Library/Logs/CrashReporter/*.ips',),
        "output_types": "standard",
        "artifact_icon": "layers",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 5527 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 0 rows",
            "belkactf6": "iOS 16.3 | 186 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 83 rows",
            "ctf2020_ios12": "iOS 12.4 | 650 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "falken_ios26": "iOS 26.2.1 | 230 rows",
            "felix23_ios16": "iOS 16.5 | 1312 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 131 rows",
            "hc_ios26": "iOS 26.5.2 | 1273 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 555 rows",
            "hickman_ios14": "iOS 14.3 | 579 rows",
            "hickman_ios15": "iOS 15.3.1 | 1047 rows",
            "iphone11_ios17": "iOS 17.3 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 0 rows",
            "jess_ios15": "iOS 15.0.2 | 118 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
        },
    },
}

import json
import os
import re
from datetime import datetime, timedelta, timezone

from scripts.ilapfuncs import artifact_processor, logfunc

_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)
_OFFSET_TS = re.compile(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})(\.\d+)?\s*([+-]\d{2})(\d{2})$')
_KIND = re.compile(r'-\d{4}-\d{2}-\d{2}-\d{6}(\.\d+)?\.ips$')
_PROC_PID = re.compile(r'^(.*?)\s*\[(\d+)\]\s*$')
_RESOURCE_KINDS = ('cpu_resource', 'wakeups_resource', 'diskwrites_resource', 'cpu_resource_fatal')
# Apple's wording for the translated Exception Note of each flag, from the JSON crash report page
_EXCEPTION_NOTES = (('isCorpse', 'EXC_CORPSE_NOTIFY'),
                    ('isNonFatal', "NON-FATAL CONDITION (this isn't a crash)"),
                    ('isSimulated', "SIMULATED (this isn't a crash)"))


def _offset_ts(text):
    """A 'YYYY-MM-DD HH:MM:SS[.frac] +HHMM' value as an aware UTC datetime, else ''."""
    m = _OFFSET_TS.match(str(text or '').strip())
    if not m:
        return ''
    try:
        base = datetime.strptime(m.group(1), '%Y-%m-%d %H:%M:%S')
        frac = (m.group(2) or '.0')[1:]
        micro = int((frac + '000000')[:6])
        sign = -1 if m.group(3).startswith('-') else 1
        offset = timedelta(hours=abs(int(m.group(3))), minutes=int(m.group(4))) * sign
        return base.replace(microsecond=micro, tzinfo=timezone(offset)).astimezone(timezone.utc)
    except (ValueError, OverflowError):
        return ''


def _epoch(value, milliseconds=False):
    """A Unix seconds (or milliseconds) value as an aware UTC datetime, else ''."""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return ''
    try:
        return _EPOCH + (timedelta(milliseconds=number) if milliseconds else timedelta(seconds=number))
    except OverflowError:
        return ''


def _as_str(value):
    if value is None:
        return ''
    if isinstance(value, bool):
        return 'True' if value else 'False'
    if isinstance(value, (list, tuple)):
        return ', '.join(_as_str(v) for v in value)
    return str(value)


def _kind_of(base):
    return _KIND.sub('', base)


def _split(path, log=True):
    """(metadata dict, body text) of an .ips file; ({}, '') when the first line is not JSON."""
    try:
        with open(path, 'rb') as handle:
            data = handle.read()
    except OSError as error:
        logfunc(f'iOS Diagnostic Reports: could not read {os.path.basename(path)}: {error}')
        return {}, ''
    first, _, rest = data.partition(b'\n')
    try:
        meta = json.loads(first.decode('utf-8', errors='replace'))
    except ValueError:
        if log:
            logfunc(f'iOS Diagnostic Reports: no JSON metadata line in {os.path.basename(path)}')
        return {}, ''
    if not isinstance(meta, dict):
        return {}, ''
    return meta, rest.decode('utf-8', errors='replace')


def _json_body(body, path):
    stripped = body.lstrip()
    if not stripped[:1] in ('{', '['):
        return None
    try:
        return json.loads(stripped)
    except ValueError as error:
        logfunc(f'iOS Diagnostic Reports: the body of {os.path.basename(path)} did not parse as JSON: {error}')
        return None


def _line(body, label):
    """The value of the first 'Label: value' line in a text body, else ''."""
    m = re.search(rf'^{re.escape(label)}:[ \t]*(.*)$', body, re.M)
    return m.group(1).strip() if m else ''


def _proc_pid(text):
    m = _PROC_PID.match(text or '')
    return (m.group(1).strip(), m.group(2)) if m else ((text or '').strip(), '')


def _ips_files(context):
    """The .ips files found, skipping directories and AppleDouble twins, each path once."""
    seen = set()
    for file_found in context.get_files_found():
        file_found = str(file_found)
        base = os.path.basename(file_found)
        if os.path.isdir(file_found) or base.startswith('._') or not base.endswith('.ips'):
            continue
        if file_found in seen:
            continue
        seen.add(file_found)
        yield file_found, base


def _process_names(report, bug_type):
    """(frontmost names, all entries) for a jetsam or stackshot body."""
    if bug_type == '298':
        entries = report.get('processes') if isinstance(report.get('processes'), list) else []
        front = [_as_str(e.get('name')) for e in entries if isinstance(e, dict) and 'frontmost' in (e.get('states') or [])]
        return front, entries
    by_pid = report.get('processByPid') if isinstance(report.get('processByPid'), dict) else {}
    front_pids = {str(p) for p in (report.get('frontmostPids') or [])}
    front = [_as_str(v.get('procname')) for k, v in by_pid.items() if str(k) in front_pids and isinstance(v, dict)]
    return front, list(by_pid.values())


@artifact_processor
def ips_reports(context):
    data_headers = (
        ('Report Time', 'datetime'),
        'Report Kind',
        'Bug Type',
        'Process or App',
        'Bundle ID',
        'App Version',
        'Build Version',
        'OS Version',
        'First Party',
        'Retired',
        'Incident ID',
        'Size Bytes',
        'Source File',
    )
    data_list = []
    sources = []
    for path, base in _ips_files(context):
        meta, body = _split(path)
        retired = os.path.basename(os.path.dirname(path)) == 'Retired'
        if not meta:
            # not a report: listed by name, size and location so the folder's contents stay complete
            data_list.append(('', base[:-4], '', '', '', '', '', '', '', retired, '', os.path.getsize(path),
                              context.get_relative_path(path)))
            sources.append(path)
            continue
        bug_type = _as_str(meta.get('bug_type'))
        bundle = _as_str(meta.get('bundleID'))
        if not bundle and bug_type == '225':
            report = _json_body(body, path)
            if isinstance(report, list):
                bundle = ', '.join(sorted({_as_str(e.get('bundleId')) for e in report if isinstance(e, dict) and e.get('bundleId')}))
        elif not bundle and bug_type == '229':
            report = _json_body(body, path)
            if isinstance(report, dict):
                setting = (report.get('settinglog') or {}).get('setting') if isinstance(report.get('settinglog'), dict) else None
                bundle = _as_str(setting.get('bundleId')) if isinstance(setting, dict) else ''
        data_list.append((
            _offset_ts(meta.get('timestamp')),
            _kind_of(base),
            bug_type,
            _as_str(meta.get('name') or meta.get('app_name')),
            bundle,
            _as_str(meta.get('app_version')),
            _as_str(meta.get('build_version')),
            _as_str(meta.get('os_version')),
            _as_str(meta.get('is_first_party')),
            retired,
            _as_str(meta.get('incident_id')),
            os.path.getsize(path),
            context.get_relative_path(path),
        ))
        sources.append(path)
    return data_headers, data_list, '\n'.join(sources)


def _crash_from_json(report):
    bundle = report.get('bundleInfo') if isinstance(report.get('bundleInfo'), dict) else {}
    exc = report.get('exception') if isinstance(report.get('exception'), dict) else {}
    term = report.get('termination') if isinstance(report.get('termination'), dict) else {}
    osv = report.get('osVersion') if isinstance(report.get('osVersion'), dict) else {}
    exc_type = _as_str(exc.get('type'))
    if exc.get('signal'):
        exc_type = f"{exc_type} ({_as_str(exc.get('signal'))})".strip()
    reason = ''
    if term:
        code = term.get('code')
        try:
            code_text = f'0x{int(code):x}'
        except (TypeError, ValueError):
            code_text = _as_str(code)
        reason = f"Namespace {_as_str(term.get('namespace'))}, Code {code_text}"
        if term.get('indicator'):
            reason += f" ({_as_str(term.get('indicator'))})"
    notes = [wording for key, wording in _EXCEPTION_NOTES if report.get(key) in (True, 'true', 'True', 1, '1')]
    version = _as_str(bundle.get('CFBundleShortVersionString'))
    if bundle.get('CFBundleVersion'):
        version = f"{version} ({_as_str(bundle.get('CFBundleVersion'))})".strip()
    parent = _as_str(report.get('parentProc'))
    if report.get('parentPid') not in (None, ''):
        parent = f"{parent} [{_as_str(report.get('parentPid'))}]".strip()
    os_version = _as_str(osv.get('train'))
    if osv.get('build'):
        os_version = f"{os_version} ({_as_str(osv.get('build'))})".strip()
    return {
        'when': _offset_ts(report.get('captureTime')), 'launch': _offset_ts(report.get('procLaunch')),
        'process': _as_str(report.get('procName')), 'pid': _as_str(report.get('pid')),
        'bundle': _as_str(bundle.get('CFBundleIdentifier')), 'version': version,
        'role': _as_str(report.get('procRole')), 'parent': parent, 'exception': exc_type,
        'note': ', '.join(notes), 'reason': reason, 'description': '',
        'model': _as_str(report.get('modelCode')), 'os': os_version, 'uptime': _as_str(report.get('uptime')),
        'locked': _as_str(report.get('isLocked')), 'unlocked': _as_str(report.get('wasUnlockedSinceBoot')),
        'incident': _as_str(report.get('incident')),
    }


def _crash_from_text(body):
    process, pid = _proc_pid(_line(body, 'Process'))
    return {
        'when': _offset_ts(_line(body, 'Date/Time')), 'launch': _offset_ts(_line(body, 'Launch Time')),
        'process': process, 'pid': pid, 'bundle': _line(body, 'Identifier'), 'version': _line(body, 'Version'),
        'role': _line(body, 'Role'), 'parent': _line(body, 'Parent Process'),
        'exception': _line(body, 'Exception Type'), 'note': _line(body, 'Exception Note'),
        'reason': _line(body, 'Termination Reason'), 'description': _line(body, 'Termination Description'),
        'model': _line(body, 'Hardware Model'), 'os': _line(body, 'OS Version'), 'uptime': '',
        'locked': '', 'unlocked': '', 'incident': _line(body, 'Incident Identifier'),
    }


@artifact_processor
def ips_app_crashes(context):
    data_headers = (
        ('Crash Time', 'datetime'),
        ('Launch Time', 'datetime'),
        'Process',
        'PID',
        'Bundle ID',
        'Version',
        'Role',
        'Parent Process',
        'Exception Type',
        'Exception Note',
        'Termination Reason',
        'Termination Description',
        'Hardware Model',
        'OS Version',
        'Time Awake Since Boot (s)',
        'Device Locked (as stored)',
        'Unlocked Since Boot (as stored)',
        'Report Form',
        'Incident ID',
        'Source File',
    )
    data_list = []
    sources = []
    for path, _base in _ips_files(context):
        meta, body = _split(path, log=False)
        bug_type = _as_str(meta.get('bug_type'))
        if bug_type not in ('109', '309'):
            continue
        if bug_type == '309':
            report = _json_body(body, path)
            if not isinstance(report, dict):
                continue
            fields = _crash_from_json(report)
            form = 'JSON'
        else:
            fields = _crash_from_text(body)
            form = 'text'
        data_list.append((
            fields['when'], fields['launch'], fields['process'], fields['pid'], fields['bundle'], fields['version'],
            fields['role'], fields['parent'], fields['exception'], fields['note'], fields['reason'],
            fields['description'], fields['model'], fields['os'], fields['uptime'], fields['locked'],
            fields['unlocked'], form, fields['incident'] or _as_str(meta.get('incident_id')),
            context.get_relative_path(path),
        ))
        sources.append(path)
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def ips_app_usage(context):
    data_headers = (
        ('Range Start', 'datetime'),
        ('Range End', 'datetime'),
        ('Event Time', 'datetime'),
        'Bundle ID',
        'Event Type',
        'Count',
        'Foreground Duration (as stored)',
        'App Version',
        'Reporting App',
        'Storefront',
        'Cohort',
        'Source File',
    )
    data_list = []
    sources = []
    for path, _base in _ips_files(context):
        meta, body = _split(path, log=False)
        if _as_str(meta.get('bug_type')) != '225':
            continue
        report = _json_body(body, path)
        if not isinstance(report, list):
            continue
        for entry in report:
            if not isinstance(entry, dict):
                continue
            data_list.append((
                _epoch(entry.get('rangeStartTime')),
                _epoch(entry.get('rangeEndTime')),
                _epoch(entry.get('eventTime'), milliseconds=True),
                _as_str(entry.get('bundleId')),
                _as_str(entry.get('eventType')),
                _as_str(entry.get('count')),
                _as_str(entry.get('foregroundDuration')),
                _as_str(entry.get('shortAppVersion')),
                _as_str(entry.get('app')),
                _as_str(entry.get('storefront')),
                _as_str(entry.get('cohort')),
                context.get_relative_path(path),
            ))
        sources.append(path)
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def ips_resource_reports(context):
    data_headers = (
        ('Start', 'datetime'),
        ('End', 'datetime'),
        'Process',
        'PID',
        'Event',
        'Action Taken',
        'Detail',
        'Duration',
        'Hardware Model',
        'OS Version',
        ('Report Time', 'datetime'),
        'Incident ID',
        'Source File',
    )
    data_list = []
    sources = []
    for path, base in _ips_files(context):
        kind = _kind_of(base)
        if not kind.endswith(_RESOURCE_KINDS):
            continue
        meta, body = _split(path, log=False)
        if not meta:
            continue
        detail = _line(body, 'Wakeups') or _line(body, 'CPU') or _line(body, 'Writes')
        data_list.append((
            _offset_ts(_line(body, 'Date/Time')),
            _offset_ts(_line(body, 'End time')),
            _line(body, 'Command') or _as_str(meta.get('app_name') or meta.get('name')),
            _line(body, 'PID'),
            _line(body, 'Event'),
            _line(body, 'Action taken'),
            detail,
            _line(body, 'Duration'),
            _line(body, 'Hardware model'),
            _line(body, 'OS Version') or _as_str(meta.get('os_version')),
            _offset_ts(meta.get('timestamp')),
            _line(body, 'Incident Identifier') or _as_str(meta.get('incident_id')),
            context.get_relative_path(path),
        ))
        sources.append(path)
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def ips_snapshot_events(context):
    data_headers = (
        ('Time', 'datetime'),
        'Kind',
        'Reason',
        'Jettisoned Process',
        'Largest Process',
        'Frontmost Processes',
        'Processes Listed',
        'Page Size',
        'OS Build',
        'Incident ID',
        'Source File',
    )
    data_list = []
    sources = []
    for path, _base in _ips_files(context):
        meta, body = _split(path, log=False)
        bug_type = _as_str(meta.get('bug_type'))
        if bug_type not in ('298', '288'):
            continue
        report = _json_body(body, path)
        if not isinstance(report, dict):
            continue
        front, entries = _process_names(report, bug_type)
        jettisoned = ''
        reason = _as_str(report.get('reason'))
        if bug_type == '298':
            for entry in entries:
                if isinstance(entry, dict) and entry.get('reason'):
                    jettisoned = _as_str(entry.get('name'))
                    reason = _as_str(entry.get('reason'))
                    break
        memory = report.get('memoryStatus') if isinstance(report.get('memoryStatus'), dict) else {}
        data_list.append((
            _offset_ts(report.get('date')),
            'jetsam event' if bug_type == '298' else 'stackshot',
            reason,
            jettisoned,
            _as_str(report.get('largestProcess')),
            ', '.join(sorted(set(front))),
            len(entries),
            _as_str(memory.get('pageSize')),
            _as_str(report.get('build')),
            _as_str(report.get('incident') or meta.get('incident_id')),
            context.get_relative_path(path),
        ))
        sources.append(path)
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def ips_snapshot_processes(context):
    data_headers = (
        ('Snapshot Time', 'datetime'),
        'Process',
        'PID',
        'States',
        'Frontmost',
        'Resident Pages',
        'Lifetime Max Pages',
        'Age (as stored)',
        'Jetsam Reason',
        'Source File',
    )
    data_list = []
    sources = []
    daemons = 0
    for path, _base in _ips_files(context):
        meta, body = _split(path, log=False)
        if _as_str(meta.get('bug_type')) != '298':
            continue
        report = _json_body(body, path)
        if not isinstance(report, dict) or not isinstance(report.get('processes'), list):
            continue
        when = _offset_ts(report.get('date'))
        for entry in report['processes']:
            if not isinstance(entry, dict):
                continue
            states = entry.get('states') if isinstance(entry.get('states'), list) else []
            if 'daemon' in states:
                daemons += 1
                continue
            data_list.append((
                when,
                _as_str(entry.get('name')),
                _as_str(entry.get('pid')),
                ', '.join(_as_str(s) for s in states),
                'frontmost' in states,
                _as_str(entry.get('rpages')),
                _as_str(entry.get('lifetimeMax')),
                _as_str(entry.get('age')),
                _as_str(entry.get('reason')),
                context.get_relative_path(path),
            ))
        sources.append(path)
    if daemons:
        logfunc(f'iOS Diagnostic Reports: {daemons} jetsam process entries in the daemon state were left out')
    return data_headers, data_list, '\n'.join(sources)
