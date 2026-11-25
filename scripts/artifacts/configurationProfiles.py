__artifacts_v2__ = {
    "configuration_profiles": {
        "name": "Configuration Profiles",
        "description": "Installed configuration profiles (profile-*.stub) in the configurationprofiles "
                       "system group container, with their payload types and install details.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-16",
        "last_update_date": "2026-11-16",
        "requirements": "none",
        "category": "Device Information",
        "notes": "Reads Library/ConfigurationProfiles in the systemgroup.com.apple.configurationprofiles "
                 "Shared/SystemGroup container (iTunes backups map SysSharedContainerDomain- to the same "
                 "path, scripts/search_files.py; not exercised on a backup here). One row per "
                 "profile-*.stub that loads as a plist dictionary; a stub that cannot be read is logged "
                 "and gets no row. Display Name, Identifier, UUID, Organization and Description are the "
                 "stub's top-level PayloadDisplayName, PayloadIdentifier, PayloadUUID, PayloadOrganization"
                 " and PayloadDescription, and Payload Types the PayloadType of each PayloadContent item, "
                 "as stored. PayloadManifest names the PayloadManifest.plist list that holds the stub's "
                 "identifier: HiddenProfiles, OrderedProfiles or 'Not in PayloadManifest'; it is blank "
                 "when the manifest is missing or unreadable, and what each list controls is not "
                 "established here. Install Date is the stub's InstallDate, a plist date read as UTC. "
                 "Data-proven on two public images: ctf2020_ios12 (iOS 12.4) and dexter_ios18 (iOS 18.3.2)"
                 " each held one stub, in HiddenProfiles, with Installed Interactively False and Removal "
                 "Stub True as stored; dexter_ios18 also carries a Carrier Name. On both, Organization, "
                 "Description and Installed By (as stored) had no value: neither stub holds a top-level "
                 "PayloadOrganization or PayloadDescription, or installedBy; Carrier Name had no value on "
                 "ctf2020_ios12. The other 20 images in sample_data held the container and no stub. Known "
                 "data on an iOS 27.2 Simulator (not a device), one unsigned Web Clip profile installed "
                 "through Settings: after the install the container held profile-<hash>.stub with "
                 "InstallDate equal to the second the install was confirmed (18:15:39 UTC for a "
                 "confirmation logged at 18:15:39.009) and to the install event in MCProfileEvents.plist; "
                 "the identifier was in OrderedProfiles, and the stub recorded Installed By "
                 "com.apple.Preferences and Installed Interactively True. In that test the removed profile"
                 " left no stub and MCProfileEvents.plist kept the install and remove events; when the "
                 "container holds MCProfileEvents.plist, Sysdiagnose - Managed Configuration Profile "
                 "Events reads it (2 rows on the Simulator copy). Removal Stub and Was Encrypted are "
                 "MCProfileIsRemovalStub and ProfileWasEncrypted as stored; on all 3 stubs seen, Removal "
                 "Stub was True and Was Encrypted was False. Downloaded profiles in phone/ are in "
                 "Configuration Profiles - Holding Tank. Not parsed here: MCProfileEvents.plist and "
                 "MCSettingsEvents.plist (read by the Sysdiagnose - Managed Configuration events "
                 "artifacts), UserSettings.plist (User Settings), and ProfileTruth.plist, "
                 "ClientTruth.plist, PayloadDependency.plist, CloudConfigurationDetails.plist, "
                 "CloudConfigurationSetAsideDetails.plist, AppAccessibilityParameters.plist, "
                 "PublicInfo/MCMeta.plist and PublicInfo/NamespacedUserSettings.plist (contents not "
                 "characterised here). Lockdown Mode is not covered; it was not tested.",
        "paths": (
            '*/systemgroup.com.apple.configurationprofiles/Library/ConfigurationProfiles/profile-*.stub',
            '*/systemgroup.com.apple.configurationprofiles/Library/ConfigurationProfiles/PayloadManifest.plist',
        ),
        "output_types": ["html", "tsv", "lava", "timeline"],
        "artifact_icon": "settings",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 0 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 0 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 0 rows",
            "ctf2020_ios12": "iOS 12.4 | 1 row",
            "dexter_ios18": "iOS 18.3.2 | 1 row",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios17_2": "iOS 17.2.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "hc_ios26": "iOS 26.5.2 | 0 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 0 rows",
            "hickman_ios14": "iOS 14.3 | 0 rows",
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
    "configuration_profiles_holding_tank": {
        "name": "Configuration Profiles - Holding Tank",
        "description": "Downloaded configuration profiles in the holding tank (phone/profile-*.pdata) of "
                       "the configurationprofiles system group container, with the time "
                       "HoldingTankManifest.plist stores for each.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-16",
        "last_update_date": "2026-11-16",
        "requirements": "none",
        "category": "Device Information",
        "notes": "One row per phone/profile-*.pdata under Library/ConfigurationProfiles in the "
                 "systemgroup.com.apple.configurationprofiles container (backup mapping as in "
                 "Configuration Profiles). Holding Tank Time is the date phone/HoldingTankManifest.plist "
                 "stores for the profile's identifier, read as UTC; what it marks is not established. "
                 "Display Name, Identifier, UUID, Organization, Description and Payload Types are read as "
                 "stored from the .pdata. A .pdata that does not load as a plist dictionary keeps a row "
                 "with Decoded 'No' and its fields blank; that path is covered by a synthetic test only, "
                 "and no signed or encrypted profile was tested. Known data on an iOS 27.2 Simulator (not "
                 "a device): a download of an unsigned Web Clip profile, made after an install and removal"
                 " of the same profile, wrote phone/profile-<hash>.pdata, byte-identical to the profile "
                 "file, with the same <hash> as the stub the earlier install created, and an entry for its"
                 " identifier in phone/HoldingTankManifest.plist. The stored time was 24 hours after the "
                 ".pdata file's modified time (the download time was not logged). Eight minutes later the "
                 ".pdata was gone and HoldingTankManifest.plist held an empty dictionary; what removed it "
                 "was not observed. No image in sample_data held a .pdata; ctf2020_ios12 and "
                 "iphone14plus_ios18_mvs2025 held a HoldingTankManifest.plist and no .pdata. Decoded held "
                 "Yes on the one Simulator row.",
        "paths": (
            '*/systemgroup.com.apple.configurationprofiles/Library/ConfigurationProfiles/phone/*',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "settings",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 0 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 0 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 0 rows",
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios17_2": "iOS 17.2.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "hc_ios26": "iOS 26.5.2 | 0 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 0 rows",
            "hickman_ios14": "iOS 14.3 | 0 rows",
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
}

import os
import plistlib
from xml.parsers.expat import ExpatError

from scripts.ilapfuncs import artifact_processor, convert_plist_date_to_utc, logfunc

_PLIST_ERRORS = (plistlib.InvalidFileException, ExpatError, ValueError, TypeError, OverflowError)


def _load(path):
    try:
        with open(path, 'rb') as handle:
            data = plistlib.load(handle)
    except _PLIST_ERRORS + (OSError,) as error:
        logfunc(f'Configuration Profiles: could not read {os.path.basename(path)}: {error}')
        return None
    return data if isinstance(data, dict) else None


def _text(value):
    return '' if value is None else str(value)


def _payload_types(profile):
    content = profile.get('PayloadContent')
    if not isinstance(content, list):
        return ''
    return ', '.join(_text(item.get('PayloadType')) for item in content if isinstance(item, dict))


def _manifest_list(manifest, identifier):
    if manifest is None:
        return ''
    if identifier in (manifest.get('HiddenProfiles') or []):
        return 'HiddenProfiles'
    if identifier in (manifest.get('OrderedProfiles') or []):
        return 'OrderedProfiles'
    return 'Not in PayloadManifest'


def _date(value):
    return convert_plist_date_to_utc(value) if hasattr(value, 'year') else ''


def _by_folder(context):
    by_dir = {}
    for path in sorted(str(f) for f in context.get_files_found() if not os.path.isdir(str(f))):
        by_dir.setdefault(os.path.dirname(path), {})[os.path.basename(path)] = path
    return by_dir


@artifact_processor
def configuration_profiles(context):
    data_list = []
    source_paths = []
    for _folder, names in sorted(_by_folder(context).items()):
        stubs = [p for n, p in sorted(names.items()) if n.startswith('profile-') and n.endswith('.stub')]
        if not stubs:
            continue
        manifest_path = names.get('PayloadManifest.plist')
        manifest = _load(manifest_path) if manifest_path else None
        for path in stubs:
            source_paths.append(path)
            profile = _load(path)
            if profile is None:
                continue
            options = profile.get('InstallOptions') if isinstance(profile.get('InstallOptions'), dict) else {}
            identifier = _text(profile.get('PayloadIdentifier'))
            data_list.append((
                _date(profile.get('InstallDate')),
                _text(profile.get('PayloadDisplayName')),
                identifier,
                _text(profile.get('PayloadUUID')),
                _text(profile.get('PayloadOrganization')),
                _text(profile.get('PayloadDescription')),
                _payload_types(profile),
                _manifest_list(manifest, identifier),
                _text(options.get('installedBy')),
                _text(options.get('isInstalledInteractively')),
                _text(options.get('carrierName')),
                _text(profile.get('MCProfileIsRemovalStub')),
                _text(profile.get('ProfileWasEncrypted')),
            ))
        if manifest_path:
            source_paths.append(manifest_path)

    data_headers = (
        ('Install Date', 'datetime'),
        'Display Name',
        'Identifier',
        'UUID',
        'Organization',
        'Description',
        'Payload Types',
        'PayloadManifest',
        'Installed By (as stored)',
        'Installed Interactively (as stored)',
        'Carrier Name',
        'Removal Stub (as stored)',
        'Was Encrypted (as stored)',
    )
    return data_headers, data_list, '\n'.join(source_paths)


@artifact_processor
def configuration_profiles_holding_tank(context):
    data_list = []
    source_paths = []
    for folder, names in sorted(_by_folder(context).items()):
        if os.path.basename(folder) != 'phone':
            continue
        pdata = [p for n, p in sorted(names.items()) if n.endswith('.pdata')]
        if not pdata:
            continue
        tank_path = names.get('HoldingTankManifest.plist')
        tank = _load(tank_path) if tank_path else None
        for path in pdata:
            source_paths.append(path)
            profile = _load(path)
            identifier = _text((profile or {}).get('PayloadIdentifier'))
            data_list.append((
                _date((tank or {}).get(identifier)) if identifier else '',
                'Yes' if profile is not None else 'No',
                _text((profile or {}).get('PayloadDisplayName')),
                identifier,
                _text((profile or {}).get('PayloadUUID')),
                _text((profile or {}).get('PayloadOrganization')),
                _text((profile or {}).get('PayloadDescription')),
                _payload_types(profile or {}),
            ))
        if tank_path:
            source_paths.append(tank_path)

    data_headers = (
        ('Holding Tank Time (as stored)', 'datetime'),
        'Decoded',
        'Display Name',
        'Identifier',
        'UUID',
        'Organization',
        'Description',
        'Payload Types',
    )
    return data_headers, data_list, '\n'.join(source_paths)
