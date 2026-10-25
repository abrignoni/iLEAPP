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
            "MCSettingsEvents.plist is a copy of a file of the configuration profile service "
            "(systemgroup.com.apple.configurationprofiles/Library/ConfigurationProfiles). Its top-level "
            "keys in the tested files are EffectiveSettings, Restrictions, SystemClientRestrictions, "
            "SystemProfileRestrictions and SystemSettings. One row per dictionary in the file that holds "
            "an event, a process and a timestamp. Section is the top-level key and Path is the chain of "
            "keys below it, for example restrictedBool > allowDictation > value. Event is the stored "
            "event word (set or remove in the tested files), Process is the stored process name and "
            "Timestamp is the stored time, taken as UTC because property list dates are UTC. The file "
            "does not say what the process did beyond the event word, and a remove event is the record "
            "of a value being removed, not of the setting having been used. Each field holds "
            "one event, so the file shows one event per setting field and is not a sequence of "
            "changes; 431 rows shared 23 distinct timestamps in the tested file, because several settings "
            "carry the same time where one process wrote them together. Settings with no "
            "event are not listed, and a setting missing here is not evidence that it never changed. "
            "Observed on three sysdiagnoses: two iOS 26.6 (23G71) of one device and one iOS 26.6.2 (23G90) of another device. Earlier iOS versions were not checked."
        ),
        "paths": (
            '*/MCSettingsEvents.plist',
            '*/sysdiagnose_*.tar.gz',
        ),
        "output_types": ["html", "tsv", "lava", "timeline"],
        "artifact_icon": "settings",
        "sample_data": {
            "local_sysdiag_ios26_6_a1": "iOS 26.6 sysdiagnose | 431 rows",
            "local_sysdiag_ios26_6_a2": "iOS 26.6 sysdiagnose | 431 rows",
            "local_sysdiag_ios26_6_2_b": "iOS 26.6.2 sysdiagnose | 376 rows",
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
            "device with 2 entries; 10 entries on the iOS 26.6.2 device). Source File and Profile Identifier each separate the two tested files, which is a coincidence, "
            "since Source File is what separates the copies when more than one sysdiagnose is read. Earlier iOS versions were not checked."
        ),
        "paths": (
            '*/MCProfileEvents.plist',
            '*/sysdiagnose_*.tar.gz',
        ),
        "output_types": ["html", "tsv", "lava", "timeline"],
        "artifact_icon": "certificate",
        "sample_data": {
            "local_sysdiag_ios26_6_a1": "iOS 26.6 sysdiagnose | 2 rows",
            "local_sysdiag_ios26_6_a2": "iOS 26.6 sysdiagnose | 2 rows",
            "local_sysdiag_ios26_6_2_b": "iOS 26.6.2 sysdiagnose | 10 rows",
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
