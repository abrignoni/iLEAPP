__artifacts_v2__ = {
    "user_settings": {
        "name": "Sysdiagnose - User Settings",
        "description": "Boolean values under restrictedBool in the MCState UserSettings.plist of a sysdiagnose, as stored",
        "author": "@Hexordia",
        "creation_date": "2026-09-01",
        "last_update_date": "2026-09-18",
        "requirements": "none",
        "category": "Sysdiagnose - Settings & Preferences",
        "notes": (
            "One row per restrictedBool entry, value as stored (True, False, or empty when unset). "
            "The file is MCState's record of restriction values, and a copy inside a sysdiagnose is "
            "the file as it stood when the sysdiagnose was taken. The seven test sysdiagnoses (iOS "
            "13.3.1 to 26) held 176 to 272 entries each; the MCState/User copy held an empty "
            "dictionary on all seven and is not read."
        ),
        "paths": (
            '*/MCState/Shared/UserSettings.plist',
            '*/sysdiagnose_*.tar.gz',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "settings",
        "sample_data": {
            "ai16_ios26_sysdiag": "iOS 26.5.2 sysdiagnose | 272 rows",
            "hc_ios26_sysdiag": "iOS 26 sysdiagnose | 272 rows",
            "rodeo_ios17_sysdiag": "iOS 17.3 sysdiagnose | 213 rows",
            "felix23_ios16": "iOS 16.5 | 418 rows",
            "hickman_ios13": "iOS 13.3.1 | 176 rows",
            "hickman_ios14": "iOS 14.3 | 193 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
        }
    },
    "user_settings_values": {
        "name": "Sysdiagnose - User Settings Values",
        "description": "Values under restrictedValue in the MCState UserSettings.plist of a sysdiagnose, as stored, with the Display Auto-Lock (maxInactivity) and Require Passcode (maxGracePeriod) entries decoded",
        "author": "@Hexordia",
        "creation_date": "2026-09-01",
        "last_update_date": "2026-09-18",
        "requirements": "none",
        "category": "Sysdiagnose - Settings & Preferences",
        "notes": (
            "One row per restrictedValue entry: value, rangeMinimum and rangeMaximum as stored (11 "
            "entries on the iOS 14.3 to 26 test sysdiagnoses, 10 on the iOS 13.3.1 one). Decoded is "
            "filled for two keys only. Scott Koenig's tests tied restrictedValue/maxInactivity in "
            "PublicEffectiveUserSettings.plist to the Display Auto-Lock choice in seconds, "
            "2147483647 for Never, and maxGracePeriod to the Require Passcode choice, 0 for "
            "Immediately, on iOS 12.4.8 to 16.0 (Reference: Scott Koenig, 'iOS Settings Display "
            "Auto-Lock & Require Passcode', DFIR Review, https://dfir.pubpub.org/pub/khnqi0ff); "
            "other values are shown as a duration. That paper read the live file. On the one full "
            "file system test image holding both, the live PublicEffectiveUserSettings.plist, "
            "EffectiveUserSettings.plist and ConfigurationProfiles/UserSettings.plist carried the "
            "same maxInactivity value, and the two packed sysdiagnoses carried the value from their "
            "own capture dates (60 in December 2022 and February 2023 against 2147483647 at the "
            "July 2023 extraction), so a sysdiagnose copy shows the setting as it stood when the "
            "sysdiagnose was taken. Values seen on the seven test sysdiagnoses: maxInactivity 60, "
            "300 and 2147483647; maxGracePeriod 0 on all seven."
        ),
        "paths": (
            '*/MCState/Shared/UserSettings.plist',
            '*/sysdiagnose_*.tar.gz',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "lock",
        "sample_data": {
            "ai16_ios26_sysdiag": "iOS 26.5.2 sysdiagnose | 11 rows",
            "hc_ios26_sysdiag": "iOS 26 sysdiagnose | 11 rows",
            "rodeo_ios17_sysdiag": "iOS 17.3 sysdiagnose | 11 rows",
            "felix23_ios16": "iOS 16.5 | 22 rows",
            "hickman_ios13": "iOS 13.3.1 | 10 rows",
            "hickman_ios14": "iOS 14.3 | 11 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
        }
    }
}

import plistlib
import tarfile
import zlib
from xml.parsers.expat import ExpatError

from scripts.ilapfuncs import artifact_processor, get_sysdiagnose_files, logfunc

_READ_ERRORS = (OSError, EOFError, tarfile.TarError, zlib.error,
                plistlib.InvalidFileException, ExpatError, ValueError)

# The Settings app choice each stored value corresponds to, from Scott Koenig's tests
# in the DFIR Review paper cited in the artifact notes; every other value is shown as
# a duration.
_NEVER = 2147483647


def _as_text(value):
    return '' if value is None else str(value)


def _duration(seconds):
    try:
        seconds = int(seconds)
    except (TypeError, ValueError):
        return ''
    parts = []
    for unit, size in (('hour', 3600), ('minute', 60), ('second', 1)):
        count, seconds = divmod(seconds, size)
        if count:
            parts.append(f'{count} {unit}' + ('s' if count != 1 else ''))
    return ' '.join(parts) if parts else '0 seconds'


def _decoded(key, value):
    if key == 'maxInactivity':
        return 'Never' if value == _NEVER else _duration(value)
    if key == 'maxGracePeriod':
        return 'Immediately' if value == 0 else _duration(value)
    return ''


def _settings(context):
    """Yield (plist, evidence path, staged path) for every MCState/Shared/UserSettings.plist.

    The archive match is by file name, so the MCState/User copy, which held an empty
    dictionary on test data, is skipped by the directory test.
    """
    for file_obj, source_path in get_sysdiagnose_files(
            context.get_files_found(), 'UserSettings.plist', text_mode=False):
        rel = context.get_relative_path(source_path)
        parts = rel.replace(' >> ', '/').split('/')
        if 'MCState' not in parts or 'Shared' not in parts:
            continue
        try:
            plist = plistlib.loads(file_obj.read())
        except _READ_ERRORS as ex:
            logfunc(f'Failed to read {rel}: {ex}')
            continue
        if isinstance(plist, dict):
            yield plist, rel, source_path


@artifact_processor
def user_settings(context):
    data_list = []
    sources = []
    for plist, rel, source_path in _settings(context):
        sources.append(source_path)
        settings = plist.get('restrictedBool')
        if not isinstance(settings, dict):
            continue
        for key, entry in settings.items():
            value = entry.get('value') if isinstance(entry, dict) else None
            data_list.append((key, _as_text(value), rel))
    data_headers = ('Setting', 'Value', 'Source File')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def user_settings_values(context):
    data_list = []
    sources = []
    for plist, rel, source_path in _settings(context):
        sources.append(source_path)
        settings = plist.get('restrictedValue')
        if not isinstance(settings, dict):
            continue
        for key, entry in settings.items():
            if not isinstance(entry, dict):
                entry = {}
            value = entry.get('value')
            data_list.append((key, _as_text(value), _decoded(key, value),
                              _as_text(entry.get('rangeMinimum')),
                              _as_text(entry.get('rangeMaximum')), rel))
    data_headers = ('Setting', 'Value', 'Decoded', 'Range Minimum', 'Range Maximum',
                    'Source File')
    return data_headers, data_list, '\n'.join(sources)
