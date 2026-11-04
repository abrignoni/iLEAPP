__artifacts_v2__ = {
    "mc_settings_events": {
        "name": "Sysdiagnose - Managed Configuration Settings Events",
        "description": "Set and remove events recorded per setting in MCSettingsEvents.plist of a sysdiagnose "
                       "(MCState/Shared), with the process named and the time of each event, as stored",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-25",
        "last_update_date": "2026-10-25",
        "requirements": "none",
        "category": "Sysdiagnose - Settings & Preferences",
        "notes": (
            "MCSettingsEvents.plist sits under logs/MCState/Shared in the sysdiagnose; the sysdiagnose does not record where on the device it was copied from. Its top-level "
            "keys in the tested files are EffectiveSettings, Restrictions, SystemClientRestrictions, "
            "SystemProfileRestrictions and SystemSettings. One row per dictionary in the file that holds "
            "an event, a process and a timestamp. Section is the top-level key and Path is the chain of "
            "keys below it, for example restrictedBool > allowDictation > value. Event is the stored "
            "event word (set or remove in the tested files), Process is the stored process name and "
            "Timestamp is the stored time, taken as UTC because property list dates are UTC. The file "
            "does not say what the process did beyond the event word, and a remove event is the record "
            "of a value being removed, not of the setting having been used. Each field holds "
            "one event, so the file shows one event per setting field and is not a sequence of "
            "changes; 431 rows shared 23 distinct timestamps in the tested file, several settings carry the same time. Settings with no "
            "event are not listed, and a setting missing here is not evidence that it never changed. "
            "Observed on three sysdiagnoses: two iOS 26.6 (23G71) of one device and one iOS 26.6.2 (23G90) of another device. On five corpus sysdiagnoses (iOS 13.3.1, 14.3, 17.3, 26.5.2 and 26.6 build 23G71) the artifact ran without error and reported the rows listed in sample_data."
        ),
        "paths": (
            '*/MCSettingsEvents.plist',
            '*/sysdiagnose_*.tar.gz', '*/*_sysdiagnose.tar.gz',
        ),
        "output_types": ["html", "tsv", "lava", "timeline"],
        "artifact_icon": "settings",
        "sample_data": {
            "hickman_ios13_sysdiag": "iOS 13.3.1 sysdiagnose | 0 rows",
            "hickman_ios14_sysdiag": "iOS 14.3 sysdiagnose | 271 rows",
            "rodeo_ios17_sysdiag": "iOS 17.3 sysdiagnose | 313 rows",
            "ai16_ios26_sysdiag": "iOS 26.5.2 sysdiagnose | 586 rows",
            "hc_ios26_sysdiag": "iOS 26.6 (23G71) sysdiagnose | 378 rows",
        },
    },
    "mc_profile_events": {
        "name": "Sysdiagnose - Managed Configuration Profile Events",
        "description": "Profile operations recorded in MCProfileEvents.plist of a sysdiagnose (MCState/Shared), with "
                       "the process named and the time, as stored",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-25",
        "last_update_date": "2026-10-25",
        "requirements": "none",
        "category": "Sysdiagnose - Settings & Preferences",
        "notes": (
            "One row per entry of the ProfileEvents list: the profile identifier (the key of the entry), "
            "and its Operation, Process and Timestamp as stored. Timestamp is a property list date, "
            "taken as UTC. The operation words are shown as stored and are not interpreted. The list "
            "can be short or empty on a device with few profile operations, and an empty result is not "
            "evidence that no profile was ever installed. Observed on three sysdiagnoses (two iOS 26.6 of one "
            "device with 2 entries; 10 entries on the iOS 26.6.2 device)."
            " On the iOS 26.6.2 file Profile Identifier held one value on every row (one profile, 10 operations). On five corpus sysdiagnoses (iOS 13.3.1, 14.3, 17.3, 26.5.2 and 26.6 build 23G71) the artifact ran without error and reported the rows listed in sample_data. MCProfileEvents.plist is present only in the iOS 26.5.2 one, with an empty ProfileEvents list."
        ),
        "paths": (
            '*/MCProfileEvents.plist',
            '*/sysdiagnose_*.tar.gz', '*/*_sysdiagnose.tar.gz',
        ),
        "output_types": ["html", "tsv", "lava", "timeline"],
        "artifact_icon": "certificate",
        "sample_data": {
            "hickman_ios13_sysdiag": "iOS 13.3.1 sysdiagnose | 0 rows",
            "hickman_ios14_sysdiag": "iOS 14.3 sysdiagnose | 0 rows",
            "rodeo_ios17_sysdiag": "iOS 17.3 sysdiagnose | 0 rows",
            "ai16_ios26_sysdiag": "iOS 26.5.2 sysdiagnose | 0 rows",
            "hc_ios26_sysdiag": "iOS 26.6 (23G71) sysdiagnose | 0 rows",
        },
    },
}

import plistlib
import tarfile
import zlib
from datetime import datetime, timezone
from xml.parsers.expat import ExpatError

from scripts.ilapfuncs import artifact_processor, get_sysdiagnose_files, logfunc

_READ_ERRORS = (OSError, EOFError, tarfile.TarError, zlib.error,
                plistlib.InvalidFileException, ExpatError, ValueError)


def _utc(value):
    if isinstance(value, datetime):
        return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)
    return ''


def _events(node, path):
    """Yield (path list, event dict) for every dict holding an event, a process and a timestamp."""
    if isinstance(node, dict):
        if 'event' in node and 'process' in node and 'timestamp' in node:
            yield path, node
            return
        for key, value in node.items():
            yield from _events(value, path + [str(key)])
    elif isinstance(node, list):
        for index, value in enumerate(node):
            yield from _events(value, path + [str(index)])


def _load(file_obj, rel):
    try:
        value = plistlib.loads(file_obj.read())
    except _READ_ERRORS as ex:
        logfunc(f'Failed to read {rel}: {ex}')
        return None
    return value if isinstance(value, dict) else None


@artifact_processor
def mc_settings_events(context):
    data_headers = (('Timestamp', 'datetime'), 'Section', 'Path', 'Event', 'Process', 'Source File')
    data_list = []
    sources = []
    for file_obj, source_path in get_sysdiagnose_files(
            context.get_files_found(), 'MCSettingsEvents.plist', text_mode=False):
        rel = context.get_relative_path(source_path)
        root = _load(file_obj, rel)
        if root is None:
            continue
        sources.append(source_path)
        for section, body in root.items():
            for path, event in _events(body, []):
                data_list.append((_utc(event.get('timestamp')), str(section), ' > '.join(path),
                                  str(event.get('event', '')), str(event.get('process', '')), rel))
    data_list.sort(key=lambda row: (str(row[0]), row[1], row[2]))
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def mc_profile_events(context):
    data_headers = (('Timestamp', 'datetime'), 'Profile Identifier', 'Operation', 'Process', 'Source File')
    data_list = []
    sources = []
    for file_obj, source_path in get_sysdiagnose_files(
            context.get_files_found(), 'MCProfileEvents.plist', text_mode=False):
        rel = context.get_relative_path(source_path)
        root = _load(file_obj, rel)
        if root is None:
            continue
        sources.append(source_path)
        entries = root.get('ProfileEvents')
        for entry in entries if isinstance(entries, list) else []:
            if not isinstance(entry, dict):
                continue
            for identifier, body in entry.items():
                if isinstance(body, dict):
                    data_list.append((_utc(body.get('Timestamp')), str(identifier),
                                      str(body.get('Operation', '')), str(body.get('Process', '')), rel))
    data_list.sort(key=lambda row: str(row[0]))
    return data_headers, data_list, '\n'.join(sources)
