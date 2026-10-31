__artifacts_v2__ = {
    "swcutil_associated_domains": {
        "name": "Sysdiagnose - Associated Domains (swcutil)",
        "description": "Entries of the DATABASE section of swcutil_show.txt in a sysdiagnose: the service, app "
                       "identifier, domain, approval states and check times of each app and domain pairing, as printed; a (null) domain is shown blank and the check times are parsed to UTC",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-25",
        "last_update_date": "2026-10-25",
        "requirements": "none",
        "category": "Sysdiagnose",
        "notes": (
            "swcutil_show.txt holds the output of the swcutil tool as a sysdiagnose captures it; its Storage line names the swc.db file the tool read (under com.apple.SharedWebCredentials on iOS 14 and later, under Library/Caches on iOS 13). One row per "
            "block of the DATABASE section, values as printed: Service (applinks, webcredentials, "
            "appclips, activitycontinuation or authsrv; the iOS 26.6.2 file also has one classificationreport and one messagefilter entry), App ID (team identifier and bundle identifier), "
            "App Version, Domain, User Approval, Site/Framework Approval and Flags. Last Checked and Next "
            "Check are the printed UTC times and are blank when the block has none. Retries and Error are present on blocks where the tool printed an error for the domain; Error "
            "keeps the first line as printed. Pattern Entries and Variable Entries count the entries "
            "of the printed Patterns and Variables lines (the patterns themselves are not copied). "
            "The header lines (PID, Storage, Generation counters, Enterprise SHA, Developer Mode) are not "
            "reported; Enterprise SHA read (null) in every tested file, and Developer Mode read no where printed (the line is absent on iOS 13.3.1). User "
            "Approval read unspecified on every one of the 1,942 tested entries, so it was constant there; on the iOS 14.3 and 17.3 corpus files one block each holds a different value, and it is kept because a user choice could change it. A row records that the service holds a pairing of an app identifier with a "
            "domain; it does not by itself establish that the app is installed now or that anything was "
            "opened from the domain, because system apps and App Clips are listed, and whether an entry outlives an uninstall is not established. "
            "Apple documents associated domains as the mechanism by which an app and a website declare "
            "each other (Apple Developer, 'Supporting associated domains'). Observed on three sysdiagnoses (1,942 entries in the iOS 26.6 files: 1,363 applinks, 383 appclips, 154 "
            "webcredentials, 39 activitycontinuation, 3 authsrv; 1,690 entries in the iOS 26.6.2 file). The corpus sysdiagnoses below add iOS 13.3.1, 14.3 and 17.3. On five corpus sysdiagnoses (iOS 13.3.1, 14.3, 17.3, 26.5.2 and 26.6 build 23G71) the artifact ran without error and reported the rows listed in sample_data."
        ),
        "paths": (
            '*/swcutil_show.txt',
            '*/sysdiagnose_*.tar.gz', '*/*_sysdiagnose.tar.gz',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "world-www",
        "sample_data": {
            "hickman_ios13_sysdiag": "iOS 13.3.1 sysdiagnose | 161 rows",
            "hickman_ios14_sysdiag": "iOS 14.3 sysdiagnose | 211 rows",
            "rodeo_ios17_sysdiag": "iOS 17.3 sysdiagnose | 1,217 rows",
            "ai16_ios26_sysdiag": "iOS 26.5.2 sysdiagnose | 1,799 rows",
            "hc_ios26_sysdiag": "iOS 26.6 (23G71) sysdiagnose | 1,178 rows",
        },
    },
    "swcutil_settings": {
        "name": "Sysdiagnose - Associated Domains Settings (swcutil)",
        "description": "Per-app settings printed in the SETTINGS section of swcutil_show.txt in a sysdiagnose, as stored",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-25",
        "last_update_date": "2026-10-25",
        "requirements": "none",
        "category": "Sysdiagnose",
        "notes": (
            "One row per key printed under an entry of the SETTINGS section, which is headed "
            "{ s = <service>, a = <app id>, d = <domain> }. Setting and Value are as printed; in the "
            "tested file the only key seen is com.apple.LaunchServices.enabled with the values 0 and 1. "
            "What the value controls is not established by the file; the key name points to Launch "
            "Services. A missing entry is not evidence of a default or of a user choice. Service and Setting were uniform on the tested files: "
            "applinks and com.apple.LaunchServices.enabled on every row. The "
            "domain part of the heading printed (null) in every tested entry and is not reported. Observed on three sysdiagnoses: two iOS 26.6 (23G71) of one device and one iOS 26.6.2 (23G90) of another device. On five corpus sysdiagnoses (iOS 13.3.1, 14.3, 17.3, 26.5.2 and 26.6 build 23G71) the artifact ran without error and reported the rows listed in sample_data."
        ),
        "paths": (
            '*/swcutil_show.txt',
            '*/sysdiagnose_*.tar.gz', '*/*_sysdiagnose.tar.gz',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "settings",
        "sample_data": {
            "hickman_ios13_sysdiag": "iOS 13.3.1 sysdiagnose | 0 rows",
            "hickman_ios14_sysdiag": "iOS 14.3 sysdiagnose | 0 rows",
            "rodeo_ios17_sysdiag": "iOS 17.3 sysdiagnose | 0 rows",
            "ai16_ios26_sysdiag": "iOS 26.5.2 sysdiagnose | 1 row",
            "hc_ios26_sysdiag": "iOS 26.6 (23G71) sysdiagnose | 0 rows",
        },
    },
}

import re
import tarfile
import zlib
from datetime import datetime, timezone

from scripts.ilapfuncs import artifact_processor, get_sysdiagnose_files, logfunc

_READ_ERRORS = (OSError, EOFError, tarfile.TarError, zlib.error)

_FIELD = re.compile(r'^([A-Za-z][A-Za-z /]*?):\s+(.*)$')
_SECTION = re.compile(r'^=+ ([A-Z ]+) =+$')
_SETTING_HEAD = re.compile(r'^\{ s = (.*?), a = (.*?), d = (.*?) \}: \{$')
_SETTING_LINE = re.compile(r'^\s+"?([^"=]+?)"? = (.*?);$')


def _entries(lines):
    """Yield (header dict, entry dict) for each block of the DATABASE section."""
    header, entry, section = {}, None, None
    for line in lines:
        match = _SECTION.match(line)
        if match:
            if entry:
                yield header, entry
            entry, section = None, match.group(1)
            continue
        if section is None:
            field = _FIELD.match(line)
            if field:
                header[field.group(1)] = field.group(2).strip()
            continue
        if section != 'DATABASE':
            continue
        if line.startswith('-----'):
            if entry:
                yield header, entry
            entry = None
            continue
        field = _FIELD.match(line)
        if field:
            if field.group(1) == 'Service':
                if entry:
                    yield header, entry
                entry = {}
            if entry is not None:
                entry[field.group(1)] = field.group(2).strip()
    if entry:
        yield header, entry


def _count_entries(text):
    """Number of top-level {...} entries on a printed Patterns or Variables line."""
    return len(re.findall(r'(?:^|, )\{', text)) if text else 0


def _ts(value):
    """A printed 'YYYY-MM-DD HH:MM:SS +0000' time as a UTC datetime; '' when absent or unreadable."""
    try:
        return datetime.strptime(value, '%Y-%m-%d %H:%M:%S %z').astimezone(timezone.utc)
    except (TypeError, ValueError):
        return ''


def _clean(value):
    return '' if value in (None, '(null)') else value


def _read_lines(file_obj, rel):
    try:
        return file_obj.read().decode('utf-8', errors='replace').splitlines()
    except _READ_ERRORS as ex:
        logfunc(f'Failed to read {rel}: {ex}')
        return None


@artifact_processor
def swcutil_associated_domains(context):
    data_headers = (
        'Service', 'App ID', 'App Version', 'Domain', 'User Approval', 'Site/Framework Approval',
        'Flags', ('Last Checked', 'datetime'), ('Next Check', 'datetime'), 'Retries', 'Error',
        'Pattern Entries', 'Variable Entries', 'Source File')
    data_list = []
    sources = []
    for file_obj, source_path in get_sysdiagnose_files(
            context.get_files_found(), 'swcutil_show.txt', text_mode=False):
        rel = context.get_relative_path(source_path)
        lines = _read_lines(file_obj, rel)
        if lines is None:
            continue
        sources.append(source_path)
        for _header, entry in _entries(lines):
            data_list.append((
                entry.get('Service', ''), entry.get('App ID', ''), entry.get('App Version', ''),
                _clean(entry.get('Domain')), entry.get('User Approval', ''),
                entry.get('Site/Fmwk Approval', ''), entry.get('Flags', ''),
                _ts(entry.get('Last Checked')), _ts(entry.get('Next Check')),
                entry.get('Retries', ''), entry.get('Error', ''),
                _count_entries(entry.get('Patterns')), _count_entries(entry.get('Variables')),
                rel))
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def swcutil_settings(context):
    data_headers = ('Service', 'App ID', 'Setting', 'Value', 'Source File')
    data_list = []
    sources = []
    for file_obj, source_path in get_sysdiagnose_files(
            context.get_files_found(), 'swcutil_show.txt', text_mode=False):
        rel = context.get_relative_path(source_path)
        lines = _read_lines(file_obj, rel)
        if lines is None:
            continue
        sources.append(source_path)
        in_settings, current = False, None
        for line in lines:
            section = _SECTION.match(line)
            if section:
                in_settings, current = section.group(1) == 'SETTINGS', None
                continue
            if not in_settings:
                continue
            head = _SETTING_HEAD.match(line)
            if head:
                current = (head.group(1), head.group(2))
                continue
            item = _SETTING_LINE.match(line)
            if item and current:
                data_list.append(current + (item.group(1), item.group(2), rel))
    return data_headers, data_list, '\n'.join(sources)
