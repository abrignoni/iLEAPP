__artifacts_v2__ = {
    "mobileInstall_installed": {
        "name": "Apps - Installed",
        "description": "Bundle IDs whose most recent installer-reported outcome in mobile_installation.log is a successful install",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-06-23",
        "last_update_date": "2026-08-25",
        "requirements": "none",
        "category": "Mobile Installation Logs",
        "notes": "Timestamps are reported as written in the log, which carries no timezone marker; in tested corpora the values were consistent with device-local time. State is set only by an installer-reported outcome: an 'Install successful' line, an 'Uninstalling identifier' line, or a 'Destroying container' line. In the tested corpora every 'Destroying container' line was written by MIUninstaller or MIUninstallNotifier. Container bookkeeping ('Made container live', written by makeContainerLiveReplacingContainer, and 'Data container moved', written by _refreshUUIDForContainer) is emitted during installs, updates and cleanup alike, so it is kept in Apps - Historical Combined and does not place a bundle here. A bundle whose install predates the retained log window has no 'Install successful' line and will not appear; absence here is not evidence that an app was never installed. The Source Event column names the line that set the state. The install kind is reported as written: Placeholder is the download stub the installer writes before the app itself installs, and Customer, System and Developer accompany the installed bundle.",
        "paths": ('**/mobile_installation.log.*', '**/sysdiagnose_*.tar.gz'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "download",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 49 rows",
            "hickman_ios13": "iOS 13.3.1 | 59 rows",
            "hickman_ios14": "iOS 14.3 | 63 rows",
            "jess_ios15": "iOS 15.0.2 | 38 rows",
            "abe_ios16": "iOS 16.5 | 45 rows",
            "felix23_ios16": "iOS 16.5 | 53 rows",
            "magnet_ios16": "iOS 16.1.1 | 64 rows",
            "felix_ios17": "iOS 17.6.1 | 54 rows",
            "fsfull002_ios17": "iOS 17.1 | 55 rows",
            "iphone11_ios17": "iOS 17.3 | 32 rows",
            "otto_ios17": "iOS 17.5.1 | 37 rows",
            "dexter_ios18": "iOS 18.3.2 | 36 rows",
            "hc_ios18_7": "iOS 18.7.8 | 36 rows",
            "iphone12_ios18": "iOS 18.7 | 58 rows",
            "iphone14plus_ios18": "iOS 18.0 | 51 rows",
            "hc_ios26": "iOS 26.5.2 | 61 rows",
        }
    },
    "mobileInstall_uninstalled": {
        "name": "Apps - Uninstalled",
        "description": "Bundle IDs whose most recent installer-reported outcome in mobile_installation.log is an uninstall or container destruction",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-06-23",
        "last_update_date": "2026-08-25",
        "requirements": "none",
        "category": "Mobile Installation Logs",
        "notes": "Timestamps are reported as written in the log, which carries no timezone marker; in tested corpora the values were consistent with device-local time. State is set only by an installer-reported outcome: an 'Install successful' line, an 'Uninstalling identifier' line, or a 'Destroying container' line. In the tested corpora every 'Destroying container' line was written by MIUninstaller or MIUninstallNotifier. Container bookkeeping ('Made container live', written by makeContainerLiveReplacingContainer, and 'Data container moved', written by _refreshUUIDForContainer) is emitted during installs, updates and cleanup alike, so it is kept in Apps - Historical Combined and does not place a bundle here. A bundle whose install predates the retained log window has no 'Install successful' line and will not appear; absence here is not evidence that an app was never installed. The Source Event column names the line that set the state. The install kind is reported as written: Placeholder is the download stub the installer writes before the app itself installs, and Customer, System and Developer accompany the installed bundle.",
        "paths": ('**/mobile_installation.log.*', '**/sysdiagnose_*.tar.gz'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "trash",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 1 row",
            "hickman_ios13": "iOS 13.3.1 | 21 rows",
            "hickman_ios14": "iOS 14.3 | 27 rows",
            "jess_ios15": "iOS 15.0.2 | 5 rows",
            "abe_ios16": "iOS 16.5 | 0 rows",
            "felix23_ios16": "iOS 16.5 | 17 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 2 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "hc_ios26": "iOS 26.5.2 | 0 rows",
        }
    },
    "mobileInstall_historical": {
        "name": "Apps - Historical Combined",
        "description": "Install, update, patch, uninstall, container and reboot events from mobile_installation.log",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-06-23",
        "last_update_date": "2026-08-25",
        "requirements": "none",
        "category": "Mobile Installation Logs",
        "notes": "Timestamps are reported as written in the log, which carries no timezone marker; in tested corpora the values were consistent with device-local time. Patch-update lines record an attempt, not a completed update. Install kinds, container personas and version strings are reported as written. Version and Short Version carry the target of a patch attempt or the version of an installable bundle; From Version carries the source of a patch attempt.",
        "paths": ('**/mobile_installation.log.*', '**/sysdiagnose_*.tar.gz'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "list",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 1003 rows",
            "hickman_ios13": "iOS 13.3.1 | 860 rows",
            "hickman_ios14": "iOS 14.3 | 798 rows",
            "jess_ios15": "iOS 15.0.2 | 940 rows",
            "abe_ios16": "iOS 16.5 | 834 rows",
            "felix23_ios16": "iOS 16.5 | 918 rows",
            "magnet_ios16": "iOS 16.1.1 | 895 rows",
            "felix_ios17": "iOS 17.6.1 | 664 rows",
            "fsfull002_ios17": "iOS 17.1 | 681 rows",
            "iphone11_ios17": "iOS 17.3 | 383 rows",
            "otto_ios17": "iOS 17.5.1 | 713 rows",
            "dexter_ios18": "iOS 18.3.2 | 763 rows",
            "hc_ios18_7": "iOS 18.7.8 | 378 rows",
            "iphone12_ios18": "iOS 18.7 | 591 rows",
            "iphone14plus_ios18": "iOS 18.0 | 910 rows",
            "hc_ios26": "iOS 26.5.2 | 455 rows",
        }
    },
    "mobileInstall_reboots": {
        "name": "State - Reboots",
        "description": "Reboot events detected in mobile_installation.log",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-06-23",
        "last_update_date": "2026-08-25",
        "requirements": "none",
        "category": "Mobile Installation Logs",
        "notes": "Timestamps are reported as written in the log, which carries no timezone marker; in tested corpora the values were consistent with device-local time.",
        "paths": ('**/mobile_installation.log.*', '**/sysdiagnose_*.tar.gz'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "refresh",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 2 rows",
            "hickman_ios13": "iOS 13.3.1 | 7 rows",
            "hickman_ios14": "iOS 14.3 | 5 rows",
            "jess_ios15": "iOS 15.0.2 | 7 rows",
            "abe_ios16": "iOS 16.5 | 4 rows",
            "felix23_ios16": "iOS 16.5 | 3 rows",
            "magnet_ios16": "iOS 16.1.1 | 7 rows",
            "felix_ios17": "iOS 17.6.1 | 2 rows",
            "fsfull002_ios17": "iOS 17.1 | 15 rows",
            "iphone11_ios17": "iOS 17.3 | 3 rows",
            "otto_ios17": "iOS 17.5.1 | 3 rows",
            "dexter_ios18": "iOS 18.3.2 | 4 rows",
            "hc_ios18_7": "iOS 18.7.8 | 26 rows",
            "iphone12_ios18": "iOS 18.7 | 6 rows",
            "iphone14plus_ios18": "iOS 18.0 | 6 rows",
            "hc_ios26": "iOS 26.5.2 | 4 rows",
        }
    },
    "mobileInstall_container_only": {
        "name": "Apps - Container Activity Only",
        "description": "Bundle IDs that mobile_installation.log mentions only through container or patch activity, with no installer-reported install or uninstall",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-25",
        "last_update_date": "2026-08-25",
        "requirements": "none",
        "category": "Mobile Installation Logs",
        "notes": "Timestamps are reported as written in the log, which carries no timezone marker; in tested corpora the values were consistent with device-local time. These bundle IDs appear in the log but never in an 'Install successful', 'Uninstalling identifier' or 'Destroying container' line, so Apps - Installed and Apps - Uninstalled do not list them. That happens when the install predates the retained log window. Presence here shows the log mentioned the bundle; it does not establish that the app was installed, and absence of an install line is not evidence that it was not. App extension bundle IDs appear here because extensions have their own containers. Parent Bundle ID (by prefix) is filled in when another bundle ID in the same log is a dotted prefix of this one, which is Apple's convention for an extension and its host app; it is read from the identifier strings, not from a relationship the log records. The Source Event column names the most recent line that mentioned the bundle.",
        "paths": ('**/mobile_installation.log.*', '**/sysdiagnose_*.tar.gz'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "box",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 92 rows",
            "hickman_ios13": "iOS 13.3.1 | 137 rows",
            "hickman_ios14": "iOS 14.3 | 157 rows",
            "jess_ios15": "iOS 15.0.2 | 534 rows",
            "abe_ios16": "iOS 16.5 | 173 rows",
            "felix23_ios16": "iOS 16.5 | 168 rows",
            "magnet_ios16": "iOS 16.1.1 | 215 rows",
            "felix_ios17": "iOS 17.6.1 | 192 rows",
            "fsfull002_ios17": "iOS 17.1 | 204 rows",
            "iphone11_ios17": "iOS 17.3 | 143 rows",
            "otto_ios17": "iOS 17.5.1 | 158 rows",
            "dexter_ios18": "iOS 18.3.2 | 145 rows",
            "hc_ios18_7": "iOS 18.7.8 | 136 rows",
            "iphone12_ios18": "iOS 18.7 | 174 rows",
            "iphone14plus_ios18": "iOS 18.0 | 169 rows",
            "hc_ios26": "iOS 26.5.2 | 160 rows",
        }
    }
}

import io
import re
import tarfile

from scripts.ilapfuncs import artifact_processor

_MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
_TAR_MEMBER_RE = re.compile(r"logs/MobileInstallation/mobile_installation\.log(\.\d+)?$")

# Only an installer-reported outcome sets a bundle's state. Container bookkeeping is
# written during installs, updates and cleanup alike, so it stays history only.
_INSTALL_PREFIX = 'Install successful'
_UNINSTALL_ACTIONS = ('Destroying container', 'Uninstalling identifier')

# 'Install Successful for' on every tested release to iOS 18; the tested iOS 26 images
# write 'Install successful for' and carry no capitalised form at all. The bundle id stops
# at the first ')' so a trailing '[Distributor: (null)]' is not swallowed. The kind prefix
# observed across the corpora is Placeholder, Customer, System or Developer.
_INSTALL_RE = re.compile(r"Install [Ss]uccessful for \(([A-Za-z]+):([^)]*)\)")
# Two spellings seen across the tested corpora:
#   'Destroying container with identifier <id> at <path>'         (iOS 12 to 15)
#   'Destroying container <id> with persona <persona> at <path>'  (iOS 16 onward)
# The persona is a UUID or the literal '(null)'.
_DESTROY_RE = re.compile(
    r"Destroying container (?:with identifier (?P<id_a>\S+)"
    r"|(?P<id_b>\S+) with persona (?P<persona>\S+)) at (?P<path>.+)$")
_UNINSTALL_RE = re.compile(r"Uninstalling identifier (?P<bundle>\S+)")
_DATA_CONTAINER_RE = re.compile(r"Data container for (?P<bundle>\S+) is now at (?P<path>.+)$")
_LIVE_CONTAINER_RE = re.compile(r"Made container live for (?P<bundle>\S+) at (?P<path>.+)$")
# Delta appears on every tested release from iOS 12 to iOS 18; Parallel and
# ParallelWithArchives appear from iOS 16 onward and coexist with Delta.
_PATCH_RE = re.compile(
    r"Attempting (?P<kind>[A-Za-z]+) patch update of (?P<bundle>\S+) "
    r"from (?P<from>.+?) to (?P<to_ver>\S+) \((?P<to_short>[^)]*)\)\s*$")
# Installing <MIInstallableBundle ID=x; [Persona=y,] Version=n, ShortVersion=s>
# The class is Bundle, BundlePatch or ParallelPlaceholder across the tested corpora.
_INSTALLABLE_RE = re.compile(
    r"Installing <MIInstallable(?P<kind>[A-Za-z]*) ID=(?P<bundle>[^;>]*);"
    r"(?: Persona=(?P<persona>[^,>]*),)? Version=(?P<version>[^,>]*),"
    r" ShortVersion=(?P<short>[^>]*)>")

_INSTALLABLE_LABELS = {
    'Bundle': 'Installing bundle',
    'BundlePatch': 'Installing bundle patch',
    'ParallelPlaceholder': 'Installing parallel placeholder',
}


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
    """Return (timestamp, action, bundle, persona, version, short_version, from_version, path) events."""
    events = []
    for line in lines:
        ts = _parse_timestamp(line)
        if ts is None:
            continue

        match = _INSTALL_RE.search(line)
        if match:
            events.append((ts, f'{_INSTALL_PREFIX} ({match.group(1)})', match.group(2),
                           '', '', '', '', ''))

        match = _DESTROY_RE.search(line)
        if match:
            bundle = match.group('id_a') or match.group('id_b') or ''
            events.append((ts, 'Destroying container', bundle, match.group('persona') or '',
                           '', '', '', match.group('path')))

        match = _DATA_CONTAINER_RE.search(line)
        if match:
            events.append((ts, 'Data container moved', match.group('bundle'),
                           '', '', '', '', match.group('path')))

        match = _LIVE_CONTAINER_RE.search(line)
        if match:
            events.append((ts, 'Made container live', match.group('bundle'),
                           '', '', '', '', match.group('path')))

        match = _UNINSTALL_RE.search(line)
        if match:
            events.append((ts, 'Uninstalling identifier', match.group('bundle'),
                           '', '', '', '', ''))

        if 'main: Reboot detected' in line:
            events.append((ts, 'Reboot detected', '', '', '', '', '', ''))

        match = _PATCH_RE.search(line)
        if match:
            events.append((ts, f"Attempting {match.group('kind')} patch update", match.group('bundle'),
                           '', match.group('to_ver'), match.group('to_short'),
                           match.group('from'), ''))

        match = _INSTALLABLE_RE.search(line)
        if match:
            kind = match.group('kind')
            events.append((ts, _INSTALLABLE_LABELS.get(kind, f'Installing {kind}'),
                           match.group('bundle'), match.group('persona') or '',
                           match.group('version'), match.group('short'), '', ''))
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
    # Sorting the log files fixes the order events are read in, which is what breaks
    # ties between two state-setting events written in the same second.
    for lines, source in _iter_log_lines(sorted(str(f) for f in context.get_files_found())):
        rel = context.get_relative_path(source)
        if rel not in sources:
            sources.append(rel)
        events.extend(_parse_events(lines))
    return events, ', '.join(sources)


def _latest_state_per_bundle(events):
    """Most recent installer-reported outcome per bundle id."""
    latest = {}
    for index, event in enumerate(events):
        bundle, action = event[2], event[1]
        if not bundle:
            continue
        if not (action.startswith(_INSTALL_PREFIX) or action in _UNINSTALL_ACTIONS):
            continue
        if bundle not in latest or (event[0], index) >= (latest[bundle][0][0], latest[bundle][1]):
            latest[bundle] = (event, index)
    return {bundle: event for bundle, (event, _index) in latest.items()}


def _latest_non_state_per_bundle(events, stateful):
    """Most recent event per bundle id that has no installer-reported outcome anywhere in the log."""
    latest = {}
    for index, event in enumerate(events):
        bundle = event[2]
        if not bundle or bundle in stateful:
            continue
        if bundle not in latest or (event[0], index) >= (latest[bundle][0][0], latest[bundle][1]):
            latest[bundle] = (event, index)
    return {bundle: event for bundle, (event, _index) in latest.items()}


def _parent_by_prefix(bundle, all_bundles):
    """The longest other bundle id in the same log that this one extends with a dot.

    Apple's convention is that an app extension's bundle id extends its host app's, so
    this is a string relationship read off the ids, not a link the log records.
    """
    best = ''
    for candidate in all_bundles:
        if candidate != bundle and bundle.startswith(candidate + '.') and len(candidate) > len(best):
            best = candidate
    return best


@artifact_processor
def mobileInstall_installed(context):
    data_headers = ('Last Installed', 'Bundle ID', 'Source Event')
    events, source = _events_and_source(context)
    data_list = [(ev[0], ev[2], ev[1]) for ev in _latest_state_per_bundle(events).values()
                 if ev[1].startswith(_INSTALL_PREFIX)]
    return data_headers, data_list, source


@artifact_processor
def mobileInstall_uninstalled(context):
    data_headers = ('Last Uninstalled', 'Bundle ID', 'Source Event')
    events, source = _events_and_source(context)
    data_list = [(ev[0], ev[2], ev[1]) for ev in _latest_state_per_bundle(events).values()
                 if ev[1] in _UNINSTALL_ACTIONS]
    return data_headers, data_list, source


@artifact_processor
def mobileInstall_historical(context):
    data_headers = ('Timestamp', 'Event', 'Bundle ID', 'Persona', 'Version', 'Short Version',
                    'From Version', 'Event Path')
    events, source = _events_and_source(context)
    return data_headers, events, source


@artifact_processor
def mobileInstall_reboots(context):
    data_headers = ('Timestamp (Local Time)', 'Description')
    events, source = _events_and_source(context)
    data_list = [(ev[0], ev[1]) for ev in events if ev[1] == 'Reboot detected']
    return data_headers, data_list, source


@artifact_processor
def mobileInstall_container_only(context):
    data_headers = ('Last Seen', 'Bundle ID', 'Parent Bundle ID (by prefix)', 'Source Event')
    events, source = _events_and_source(context)
    stateful = set(_latest_state_per_bundle(events))
    remaining = _latest_non_state_per_bundle(events, stateful)
    all_bundles = {ev[2] for ev in events if ev[2]}
    data_list = [(ev[0], ev[2], _parent_by_prefix(ev[2], all_bundles), ev[1])
                 for ev in remaining.values()]
    return data_headers, data_list, source
