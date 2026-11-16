__artifacts_v2__ = {
    "configuration_profiles": {
        "name": "Configuration Profiles",
        "description": "Configuration profiles held in the configurationprofiles system group container: "
                       "installed profiles (profile-*.stub) and downloaded profiles waiting to be "
                       "installed (phone/profile-*.pdata), with their payload types and install details.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-16",
        "last_update_date": "2026-11-16",
        "requirements": "none",
        "category": "Configuration Profiles",
        "notes": "Reads Library/ConfigurationProfiles in the systemgroup.com.apple.configurationprofiles "
                 "Shared/SystemGroup container (iTunes backups map SysSharedContainerDomain- to the same "
                 "path, scripts/search_files.py; not exercised on a backup here). One row per "
                 "profile-*.stub (State 'Installed') and per phone/profile-*.pdata (State 'Downloaded, not"
                 " installed'). Payload fields (Display Name, Identifier, UUID, Organization, Description,"
                 " the PayloadType of each PayloadContent item) are read as stored from the stub or the "
                 "downloaded profile; a .pdata that is not a plain plist (for example a signed profile) "
                 "keeps a row with its fields blank and is not decoded. PayloadManifest says whether the "
                 "stub's identifier is in PayloadManifest.plist HiddenProfiles ('Hidden') or "
                 "OrderedProfiles ('Listed'), as stored. Data-proven on two public images: ctf2020_ios12 "
                 "(iOS 12.4) and dexter_ios18 (iOS 18.3.2) each held one installed stub, Hidden, Installed"
                 " Interactively False and Removal Stub True as stored; dexter_ios18 also carries a "
                 "Carrier Name. On both, Holding Tank Time, Organization, Description and Installed By (as"
                 " stored) had no value, because neither stub holds PayloadOrganization, "
                 "PayloadDescription or installedBy and nothing was in the holding tank; Carrier Name had "
                 "no value on ctf2020_ios12. The other 20 images in sample_data held the container and no "
                 "stub or .pdata. Known data on an iOS 27.2 Simulator (not a device), with an unsigned Web"
                 " Clip profile installed through Settings: downloading it wrote "
                 "phone/profile-<hash>.pdata (the profile as a plist) and phone/HoldingTankManifest.plist;"
                 " installing it moved the profile to profile-<hash>.stub with InstallDate equal to the "
                 "second the install was confirmed (18:15:39 UTC for a confirmation logged at "
                 "18:15:39.009) and to the install event in MCProfileEvents.plist, listed it in "
                 "OrderedProfiles, and recorded Installed By com.apple.Preferences and Installed "
                 "Interactively True; removing it deleted the stub, while MCProfileEvents.plist kept the "
                 "install and remove events. Holding Tank Time is the date HoldingTankManifest.plist "
                 "stores for the identifier; in that test it was 24 hours after the download, and what it "
                 "marks is not established. Removal Stub and Was Encrypted are MCProfileIsRemovalStub and "
                 "ProfileWasEncrypted as stored; Removal Stub was True on every stub seen, the "
                 "user-installed one included. Removed profiles have no stub; their install and remove "
                 "events are in Sysdiagnose - Managed Configuration Profile Events. Not read here: "
                 "MCProfileEvents.plist and MCSettingsEvents.plist (read by the Sysdiagnose - Managed "
                 "Configuration events artifacts), UserSettings.plist (User Settings), ProfileTruth.plist,"
                 " ClientTruth.plist and PayloadDependency.plist (restriction and dependency bookkeeping),"
                 " and CloudConfigurationDetails.plist (device enrollment state, a separate item). "
                 "Lockdown Mode is not covered: no corpus image held LDMGlobalEnabled and the Simulator "
                 "offers no Lockdown Mode setting to test.",
        "paths": (
            '*/systemgroup.com.apple.configurationprofiles/Library/ConfigurationProfiles/profile-*.stub',
            '*/systemgroup.com.apple.configurationprofiles/Library/ConfigurationProfiles/PayloadManifest.plist',
            '*/systemgroup.com.apple.configurationprofiles/Library/ConfigurationProfiles/phone/*',
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
}

import os
import plistlib
from xml.parsers.expat import ExpatError

from scripts.ilapfuncs import artifact_processor, convert_plist_date_to_utc, logfunc

_PLIST_ERRORS = (plistlib.InvalidFileException, ExpatError, ValueError, TypeError, OverflowError)
_INSTALLED = 'Installed'
_DOWNLOADED = 'Downloaded, not installed'


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


def _manifest_state(manifest, identifier):
    if manifest is None:
        return ''
    if identifier in (manifest.get('HiddenProfiles') or []):
        return 'Hidden'
    if identifier in (manifest.get('OrderedProfiles') or []):
        return 'Listed'
    return 'Not in PayloadManifest'


def _date(value):
    return convert_plist_date_to_utc(value) if hasattr(value, 'year') else ''


@artifact_processor
def configuration_profiles(context):
    files = sorted(str(f) for f in context.get_files_found() if not os.path.isdir(str(f)))
    by_dir = {}
    for path in files:
        by_dir.setdefault(os.path.dirname(path), []).append(path)

    data_list = []
    source_paths = []
    for folder, paths in sorted(by_dir.items()):
        names = {os.path.basename(p): p for p in paths}
        if os.path.basename(folder) == 'phone':
            tank = _load(names['HoldingTankManifest.plist']) if 'HoldingTankManifest.plist' in names else None
            for name, path in sorted(names.items()):
                if not name.endswith('.pdata'):
                    continue
                source_paths.append(path)
                profile = _load(path)
                identifier = _text((profile or {}).get('PayloadIdentifier'))
                state = _DOWNLOADED if profile is not None else _DOWNLOADED + '; file not decoded (not a plain plist)'
                data_list.append((
                    '',
                    _date((tank or {}).get(identifier)) if identifier else '',
                    state,
                    _text((profile or {}).get('PayloadDisplayName')),
                    identifier,
                    _text((profile or {}).get('PayloadUUID')),
                    _text((profile or {}).get('PayloadOrganization')),
                    _text((profile or {}).get('PayloadDescription')),
                    _payload_types(profile or {}),
                    '', '', '', '', '', '',
                ))
            if tank is not None:
                source_paths.append(names['HoldingTankManifest.plist'])
            continue

        manifest_path = names.get('PayloadManifest.plist')
        manifest = _load(manifest_path) if manifest_path else None
        stubs = [p for n, p in sorted(names.items()) if n.startswith('profile-') and n.endswith('.stub')]
        for path in stubs:
            source_paths.append(path)
            profile = _load(path)
            if profile is None:
                continue
            options = profile.get('InstallOptions') if isinstance(profile.get('InstallOptions'), dict) else {}
            identifier = _text(profile.get('PayloadIdentifier'))
            data_list.append((
                _date(profile.get('InstallDate')),
                '',
                _INSTALLED,
                _text(profile.get('PayloadDisplayName')),
                identifier,
                _text(profile.get('PayloadUUID')),
                _text(profile.get('PayloadOrganization')),
                _text(profile.get('PayloadDescription')),
                _payload_types(profile),
                _manifest_state(manifest, identifier),
                _text(options.get('installedBy')),
                _text(options.get('isInstalledInteractively')),
                _text(options.get('carrierName')),
                _text(profile.get('MCProfileIsRemovalStub')),
                _text(profile.get('ProfileWasEncrypted')),
            ))
        if stubs and manifest_path:
            source_paths.append(manifest_path)

    data_headers = (
        ('Install Date', 'datetime'),
        ('Holding Tank Time (as stored)', 'datetime'),
        'State',
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
