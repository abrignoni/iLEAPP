#!/usr/bin/env python3
"""Build a SYNTHETIC ``logs/ManagedSettings`` tree (fabricated identifiers, no data from any device).

The structure mirrors what the managedSettings artifact reads in an iOS 26 and an iOS 27 sysdiagnose:
``User`` and ``System`` scopes, a ``SettingRecords.plist`` and a ``DataVersion.plist`` per scope, an
``EffectiveSettings.plist`` for the user scope and, per client folder, one ``<store identifier>.plist``
per store with a ``.tokenized.plist`` twin and a ``clientEffectiveSettings.plist``. App and category
identifiers are ``com.example.*`` and ``SYNTH-CAT-*``; every UUID derives from a fixed namespace, so
the output is reproducible. The two variants differ in the store names they hold, the way the two
sysdiagnoses compared in the contribution notes do.

    python synthetic_managed_settings.py ios27 out.tar.gz
    python synthetic_managed_settings.py ios26 out.tar.gz

``build_files(variant)`` returns {path below logs/ManagedSettings: bytes}; ``edge_files()`` returns the
unusual files the tests add (an unreadable file, a store with no setting key, an unknown key).
"""

import io
import plistlib
import sys
import tarfile
import uuid

_NS = uuid.UUID("87654321-4321-8765-4321-876543218765")
TOKEN_KEY = bytes(range(32))                       # fabricated key material, must never be copied
BUILDS = {"ios27": "24A437", "ios26": "23G71"}


def _uid(label):
    return str(uuid.uuid5(_NS, label)).upper()


uid = _uid


def _plist(obj):
    return plistlib.dumps(obj, fmt=plistlib.PlistFormat.FMT_BINARY)


def _store(name, active, sync, version=3, **settings):
    out = {"StoreName": name, "Properties": {"active": active, "syncToWatch": sync}, "version": version}
    out.update(settings)
    return out


def _restrictions(denied):
    return {
        "appStore.denyAppStoreAppInstallation": denied,
        "appStore.denyMarketplaceAppInstallation": False,
        "appStore.denyWebDistributionAppInstallation": False,
        "appStore.maximumRating": 200 if denied else 1000,
        "webContent.blockedByFilter": {"policy": 1, "neverAllow": []},
        "webContent.limitWebProxies": False,
        "userSafety.scanningPolicy": {},
    }


def _intelligence(siri_denied):
    return {
        "siri.denySiri": siri_denied,
        "siri.denySiri3489": False,
        "siri.forceSiriReduceSensitiveContent": False,
        "intelligence.denyExternalIntelligenceIntegrations": False,
        "intelligence.denyGenmoji": siri_denied,
        "intelligence.denyImagePlayground": False,
        "intelligence.denyImageWand": False,
        "intelligence.denyPhotorealisticImageGeneration": False,
        "eyeRelief.forceScreenDistanceOn": False,
    }


def _shield(index):
    return {
        "shield.applicationCategories": {
            "activities": [{"bundleIdentifier": f"com.example.shielded{index}"},
                           {"bundleIdentifier": f"com.example.shielded{index + 1}"}],
            "categories": [{"identifier": "SYNTH-CAT-1"}, {"identifier": "SYNTH-CAT-2"}],
        },
        "shield.webDomainCategories": {"activities": [], "categories": [{"identifier": "SYNTH-CAT-1"}]},
        "screenTime.categoryShieldPolicies": [
            {"key": {"identifier": "SYNTH-CAT-1"}, "value": "warn"},
            {"key": {"identifier": "SYNTH-CAT-2"}, "value": "block"}],
    }


def _scanning():
    return {"userSafety.scanningPolicy": {
        "onServices": ["photos", "messages"], "offServices": [], "onApplications": [], "offApplications": []}}


# client folder -> [(store name, active, sync, settings)]
def _layout(variant):
    if variant == "ios27":
        return {
            "com.apple.ScreenTimeSettings": [
                ("ContentAndPrivacy", True, False, {**_intelligence(True), **_restrictions(False)}),
                ("Restrictions", True, False, _restrictions(True))],
            "com.apple.ScreenTimeSettings.TimeAllowances": [
                ("defaultGroup", False, True, _shield(1)),
                ("downtime", False, False, _shield(3)),
                ("bedtime", False, False, {})],
            "com.apple.UserSafety": [("UserSafety", True, False, {})],
            "com.apple.Preferences": [("UserSafety", False, True, _scanning())],
            "FamilyControlsAgent": [("Default", True, False,
                                     {"managedSettings.tokenEncodingKey": TOKEN_KEY,
                                      "managedSettings.tokenDecodingKeys": [TOKEN_KEY]})],
        }
    return {
        "com.apple.ScreenTime": [
            ("Default", True, False, {"deviceActivity.shareAcrossDevices": True}),
            ("SafariStore", True, False, {"safari.denyHistoryClearing": False, "safari.denyPrivateBrowsing": True}),
            ("UserSafetyStore", True, False, {"userSafety.scanningPolicy": {}})],
        "com.apple.UserSafety": [("UserSafety", True, False, {
            "userSafety.allowedClients": [{"bundleIdentifier": "com.example.camera"},
                                          {"bundleIdentifier": "com.example.photos"}]})],
        "com.apple.Preferences": [("UserSafety", False, True, _scanning())],
        "com.apple.momentsd": [("DeviceActivityStore", True, False, {
            "deviceActivity.allowedClients": [{"bundleIdentifier": "com.example.moments"}]})],
        "FamilyControlsAgent": [("Default", True, False, {"deviceActivity.allowedClients": []})],
    }


def build_files(variant):
    """{path below logs/ManagedSettings: bytes} for 'ios27' or 'ios26'."""
    layout = _layout(variant)
    files = {"System/DataVersion.plist": _plist({"version": 8}), "System/SettingRecords.plist": _plist([]),
             "User/DataVersion.plist": _plist({"version": 8})}
    records = []
    effective = {"version": 3}
    for client, stores in layout.items():
        directory = {}
        client_settings = {"version": 3}
        for name, active, sync, settings in stores:
            identifier = _uid(f"{variant}/{client}/{name}")
            directory[name] = {"identifier": identifier, "version": 2, "active": active, "syncToWatch": sync}
            files[f"User/{client}/{identifier}.plist"] = _plist(_store(name, active, sync, **settings))
            files[f"User/{client}/{identifier}.tokenized.plist"] = _plist(
                _store(name, active, sync, **{"managedSettings.tokenEncodingKey": TOKEN_KEY}))
            client_settings.update(settings)
        files[f"User/{client}/clientEffectiveSettings.plist"] = _plist(client_settings)
        effective.update({k: v for k, v in client_settings.items() if k != "version"})
        records.append({"recordIdentifier": _uid(f"{variant}/{client}/record"),
                        "containerPath": {"relative": f"file:///var/mobile/Library/example/Records/{client}"},
                        "client": {"containerIdentifier": client, "teamIdentifier": "Apple", "isInternal": True},
                        "version": 1, "storeDirectory": directory})
    # a record with no store entry, and a store entry whose file is not in the archive
    records.append({"recordIdentifier": _uid(f"{variant}/empty"),
                    "containerPath": {"relative": "file:///var/mobile/Library/example/Records/empty"},
                    "client": {"containerIdentifier": "com.example.empty", "teamIdentifier": "Apple",
                               "isInternal": False},
                    "version": 1, "storeDirectory": {}})
    records.append({"recordIdentifier": _uid(f"{variant}/missing"),
                    "containerPath": {"relative": "file:///var/mobile/Library/example/Records/missing"},
                    "client": {"containerIdentifier": "com.example.missing", "teamIdentifier": "Apple",
                               "isInternal": False},
                    "version": 1, "storeDirectory": {"Default": {
                        "identifier": _uid(f"{variant}/missing/Default"), "version": 2, "active": True,
                        "syncToWatch": False}}})
    files["User/SettingRecords.plist"] = _plist(records)
    files["User/EffectiveSettings.plist"] = _plist(effective)
    return files


def edge_files():
    """Unusual inputs: an unreadable store, a store with an unknown key, and a store with an extra Properties key."""
    return {
        f"User/com.example.broken/{_uid('broken')}.plist": b"this is not a property list",
        f"User/com.example.future/{_uid('future')}.plist": _plist(
            {"StoreName": "FutureStore", "Properties": {"active": True, "syncToWatch": False, "extra": 1},
             "version": 9, "example.futureKey": {"b": [1, 2], "a": "x"}, "example.when": 5}),
    }


LIVE_USER = "private/var/mobile/Library/com.apple.ManagedSettings"
LIVE_SYSTEM = f"private/var/containers/Shared/SystemGroup/{_uid('system-group')}/Library/com.apple.ManagedSettings.system"


def build_live_files(variant):
    """The same stores in the layout of a full file system extraction: {path below the root: bytes}.

    Store files are Records/<record identifier>/<store identifier>/detokenized.plist and hold the
    setting keys and version without StoreName or Properties, beside a tokenized.plist twin that
    carries the key material. Adds a record folder that SettingRecords.plist does not list, and two
    near-miss files whose names contain ManagedSettings.
    """
    sysdiag = build_files(variant)
    records = plistlib.loads(sysdiag["User/SettingRecords.plist"])
    files = {f"{LIVE_USER}/DataVersion.plist": _plist({"version": 7}),
             f"{LIVE_USER}/EffectiveSettings.plist": sysdiag["User/EffectiveSettings.plist"],
             f"{LIVE_USER}/Records/SettingRecords.plist": sysdiag["User/SettingRecords.plist"],
             f"{LIVE_SYSTEM}/DataVersion.plist": _plist({"version": 7}),
             f"{LIVE_SYSTEM}/Records/SettingRecords.plist": _plist([])}
    for record in records:
        client = record["client"]["containerIdentifier"]
        base = f"{LIVE_USER}/Records/{record['recordIdentifier']}"
        if f"User/{client}/clientEffectiveSettings.plist" in sysdiag:
            files[f"{base}/clientEffectiveSettings.plist"] = sysdiag[f"User/{client}/clientEffectiveSettings.plist"]
        for entry in record["storeDirectory"].values():
            stored = sysdiag.get(f"User/{client}/{entry['identifier']}.plist")
            if stored is None:
                continue
            settings = {k: v for k, v in plistlib.loads(stored).items() if k not in ("StoreName", "Properties")}
            files[f"{base}/{entry['identifier']}/detokenized.plist"] = _plist(settings)
            files[f"{base}/{entry['identifier']}/tokenized.plist"] = _plist(
                {"version": 3, "managedSettings.tokenEncodingKey": TOKEN_KEY, "decoy": True})
    orphan = f"{LIVE_USER}/Records/{_uid('orphan-record')}"
    files[f"{orphan}/clientEffectiveSettings.plist"] = _plist({"version": 3, "siri.denySiri": True})
    files[f"{orphan}/{_uid('orphan-store')}/detokenized.plist"] = _plist({"version": 3, "siri.denySiri": True})
    files["private/var/mobile/Library/com.apple.managedconfiguration.ManagedSettingsExtension/"
          "PreviousSettings.plist"] = _plist({"version": 3, "decoy": True})
    files["private/var/mobile/Library/Preferences/com.apple.remotemanagement.ManagedSettingsSubscriber.plist"] = \
        _plist({"version": 3, "decoy": True})
    return files


def write_archive(path, variant, extra=None, with_noise=True):
    """Write a sysdiagnose-shaped .tar.gz; with_noise adds an AppleDouble sidecar and an out-of-place copy."""
    root = f"sysdiagnose_SYNTHETIC_iPhone-OS_iPhone_{BUILDS[variant]}"
    files = {f"{root}/logs/ManagedSettings/{name}": data for name, data in build_files(variant).items()}
    for name, data in (extra or {}).items():
        files[f"{root}/logs/ManagedSettings/{name}"] = data
    if with_noise:
        files[f"{root}/logs/ManagedSettings/User/._EffectiveSettings.plist"] = b"\x00\x05\x16\x07"
        files[f"{root}/other/ManagedSettings/User/EffectiveSettings.plist"] = _plist({"version": 3, "decoy": True})
    with tarfile.open(path, "w:gz") as tar:
        for name in sorted(files):
            info = tarfile.TarInfo(name)
            info.size = len(files[name])
            info.mtime = 1799970000
            tar.addfile(info, io.BytesIO(files[name]))
    return path


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in BUILDS:
        sys.exit("usage: synthetic_managed_settings.py ios27|ios26 output.tar.gz")
    write_archive(sys.argv[2], sys.argv[1], edge_files())
