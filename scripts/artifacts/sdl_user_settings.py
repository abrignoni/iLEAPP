__artifacts_v2__ = {
    "user_settings": {
        "name": "User Settings",
        "description": "Boolean values under restrictedBool in UserSettings.plist, from the live ConfigurationProfiles copy of a full file system extraction or iTunes backup and the MCState copy of a sysdiagnose, as stored",
        "author": "@Hexordia",
        "creation_date": "2026-09-01",
        "last_update_date": "2026-10-31",
        "requirements": "none",
        "category": "Sysdiagnose - Settings & Preferences",
        "notes": (
            "One row per restrictedBool entry, value as stored (True, False, or empty when unset). "
            "The sysdiagnose copy sits under MCState/Shared; both copies hold restrictedBool and "
            "restrictedValue dictionaries, and a copy inside a sysdiagnose is "
            "the file as it stood when the sysdiagnose was taken. The seven test sysdiagnoses (iOS "
            "13.3.1 to 26) held 176 to 272 entries each; the MCState/User copy held an empty "
            "dictionary on all seven and is not read."
            " A full file system extraction holds the live copy at "
            "Library/ConfigurationProfiles/UserSettings.plist in the "
            "systemgroup.com.apple.configurationprofiles Shared/SystemGroup container (named so by "
            "its folder or by its .com.apple.mobile_container_manager.metadata.plist on the images "
            "read), an iTunes backup carries the file at the same path, and both are read too; a "
            "sysdiagnose kept inside the extraction adds its own MCState copy, so such an image gives"
            " one set of rows per copy, told apart by Source File. On the 17 full file system images "
            "and one iTunes backup checked (felix23_ios16 was not among them), the live copy held 170"
            " to 272 restrictedBool and 10 or 11 "
            "restrictedValue entries, and the per-user "
            "Library/UserConfigurationProfiles/UserSettings.plist held empty dictionaries on all 18 "
            "and is not read. On all 18 the live copy, EffectiveUserSettings.plist and "
            "PublicEffectiveUserSettings.plist held the same maxInactivity and maxGracePeriod values."
        ),
        "paths": (
            '*/MCState/Shared/UserSettings.plist',
            '*/Library/ConfigurationProfiles/UserSettings.plist',
            '*/sysdiagnose_*.tar.gz', '*/*_sysdiagnose.tar.gz',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "settings",
        "sample_data": {
            "ai16_ios26_sysdiag": "iOS 26.5.2 sysdiagnose | 272 rows",
            "hc_ios26_sysdiag": "iOS 26.6 sysdiagnose | 272 rows",
            "rodeo_ios17_sysdiag": "iOS 17.3 sysdiagnose | 213 rows",
            "felix23_ios16": "iOS 16.5 | 627 rows (live copy and two sysdiagnoses)",
            "hickman_ios13": "iOS 13.3.1 | 352 rows (live copy and one sysdiagnose)",
            "hickman_ios14": "iOS 14.3 | 386 rows (live copy and one sysdiagnose)",
            "magnet_ios16": "iOS 16.1.1 | 210 rows (live copy; its sysdiagnose archive is named IN_PROGRESS_ and is not read)",
            "abe_ios16": "iOS 16.5 | 210 rows",
            "belkactf6_tar": "iOS 16.3 | 210 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 224 rows",
            "ctf2020_ios12": "iOS 12.4 | 170 rows",
            "dexter_ios18": "iOS 18.3.2 | 260 rows",
            "felix_ios17": "iOS 17.6.1 | 224 rows",
            "hc_ios17_2": "iOS 17.2.1 | 214 rows",
            "hc_ios18_7": "iOS 18.7.8 | 266 rows",
            "hc_ios26": "iOS 26.5.2 | 272 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 210 rows",
            "hickman_ios14_itunes_backup_decrypted": "iOS 14.3 backup | 193 rows",
            "hickman_ios15": "iOS 15.3.1 | 203 rows",
            "iphone11_ios17": "iOS 17.3 | 213 rows",
            "iphone12_ios18": "iOS 18.7 | 266 rows",
            "otto_ios17": "iOS 17.5.1 | 224 rows",
        }
    },
    "user_settings_values": {
        "name": "User Settings Values",
        "description": "Values under restrictedValue in UserSettings.plist, from the live ConfigurationProfiles copy of a full file system extraction or iTunes backup and the MCState copy of a sysdiagnose, as stored, with the Display Auto-Lock (maxInactivity) and Require Passcode (maxGracePeriod) entries decoded",
        "author": "@Hexordia",
        "creation_date": "2026-09-01",
        "last_update_date": "2026-10-31",
        "requirements": "none",
        "category": "Sysdiagnose - Settings & Preferences",
        "notes": (
            "One row per restrictedValue entry: value, rangeMinimum and rangeMaximum as stored, "
            "rangeMaximum empty when the entry carries none (11 "
            "entries on the iOS 14.3 to 26 test sysdiagnoses, 10 on the iOS 13.3.1 one). Decoded is "
            "filled for two keys only. Scott Koenig's tests tied restrictedValue/maxInactivity in "
            "PublicEffectiveUserSettings.plist to the Display Auto-Lock choice in seconds, "
            "2147483647 for Never, and maxGracePeriod to the Require Passcode choice, 0 for "
            "Immediately, on iOS 14.4.2, with 12.4.8 and 13.5.1 also checked (Reference: Scott "
            "Koenig, 'iOS Settings Display "
            "Auto-Lock & Require Passcode', DFIR Review, https://dfir.pubpub.org/pub/khnqi0ff); "
            "other values are shown as a duration. That paper read the live file. On the one full "
            "file system test image holding both, the live PublicEffectiveUserSettings.plist, "
            "EffectiveUserSettings.plist and ConfigurationProfiles/UserSettings.plist carried the "
            "same maxInactivity value, and the two packed sysdiagnoses carried the value from their "
            "own capture dates (60 in December 2022 and February 2023 against 2147483647 at the "
            "July 2023 extraction), so a sysdiagnose copy shows the setting as it stood when the "
            "sysdiagnose was taken. Values seen on test data: maxInactivity 30, 60, 120, 180, 300 and"
            " 2147483647; maxGracePeriod 0."
            " A full file system extraction holds the live copy at "
            "Library/ConfigurationProfiles/UserSettings.plist in the "
            "systemgroup.com.apple.configurationprofiles Shared/SystemGroup container (named so by "
            "its folder or by its .com.apple.mobile_container_manager.metadata.plist on the images "
            "read), an iTunes backup carries the file at the same path, and both are read too; a "
            "sysdiagnose kept inside the extraction adds its own MCState copy, so such an image gives"
            " one set of rows per copy, told apart by Source File. On the 17 full file system images "
            "and one iTunes backup checked (felix23_ios16 was not among them), the live copy held 170"
            " to 272 restrictedBool and 10 or 11 "
            "restrictedValue entries, and the per-user "
            "Library/UserConfigurationProfiles/UserSettings.plist held empty dictionaries on all 18 "
            "and is not read. On all 18 the live copy, EffectiveUserSettings.plist and "
            "PublicEffectiveUserSettings.plist held the same maxInactivity and maxGracePeriod values."
        ),
        "paths": (
            '*/MCState/Shared/UserSettings.plist',
            '*/Library/ConfigurationProfiles/UserSettings.plist',
            '*/sysdiagnose_*.tar.gz', '*/*_sysdiagnose.tar.gz',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "lock",
        "sample_data": {
            "ai16_ios26_sysdiag": "iOS 26.5.2 sysdiagnose | 11 rows",
            "hc_ios26_sysdiag": "iOS 26.6 sysdiagnose | 11 rows",
            "rodeo_ios17_sysdiag": "iOS 17.3 sysdiagnose | 11 rows",
            "felix23_ios16": "iOS 16.5 | 33 rows (live copy and two sysdiagnoses)",
            "hickman_ios13": "iOS 13.3.1 | 20 rows (live copy and one sysdiagnose)",
            "hickman_ios14": "iOS 14.3 | 22 rows (live copy and one sysdiagnose)",
            "magnet_ios16": "iOS 16.1.1 | 11 rows (live copy; its sysdiagnose archive is named IN_PROGRESS_ and is not read)",
            "abe_ios16": "iOS 16.5 | 11 rows",
            "belkactf6_tar": "iOS 16.3 | 11 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 11 rows",
            "ctf2020_ios12": "iOS 12.4 | 10 rows",
            "dexter_ios18": "iOS 18.3.2 | 11 rows",
            "felix_ios17": "iOS 17.6.1 | 11 rows",
            "hc_ios17_2": "iOS 17.2.1 | 11 rows",
            "hc_ios18_7": "iOS 18.7.8 | 11 rows",
            "hc_ios26": "iOS 26.5.2 | 11 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 11 rows",
            "hickman_ios14_itunes_backup_decrypted": "iOS 14.3 backup | 11 rows",
            "hickman_ios15": "iOS 15.3.1 | 11 rows",
            "iphone11_ios17": "iOS 17.3 | 11 rows",
            "iphone12_ios18": "iOS 18.7 | 11 rows",
            "otto_ios17": "iOS 17.5.1 | 11 rows",
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
    """Yield (plist, evidence path, staged path) for every MCState/Shared/UserSettings.plist and
    every live Library/ConfigurationProfiles/UserSettings.plist.

    The archive match is by file name, so the MCState/User copy and the live
    Library/UserConfigurationProfiles copy, which held an empty dictionary on test data, are
    skipped by the directory test.
    """
    for file_obj, source_path in get_sysdiagnose_files(
            context.get_files_found(), 'UserSettings.plist', text_mode=False):
        rel = context.get_relative_path(source_path)
        parts = rel.replace(' >> ', '/').split('/')
        live = parts[-3:] == ['Library', 'ConfigurationProfiles', 'UserSettings.plist']
        if not live and ('MCState' not in parts or 'Shared' not in parts):
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
