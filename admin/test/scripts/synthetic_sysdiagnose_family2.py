#!/usr/bin/env python3
"""Build SYNTHETIC sysdiagnose files for the swcutil, MCState events, Network Extension, brctl and
taskinfo artifacts (sdl_swcutil, sdl_mc_events, sdl_network_extension, sdl_brctl, sdl_taskinfo).

Everything is fabricated: bundle identifiers are com.example.*, team identifiers are made up,
UUIDs are derived from a fixed namespace and times are fixed. The layouts follow the printed
layouts of the tools (swcutil show, brctl dump and container list, taskinfo) and the property list
layouts of MCSettingsEvents.plist, MCProfileEvents.plist and com.apple.networkextension.plist
(an NSKeyedArchiver archive), reduced to the parts the artifacts read plus a few lines they must
skip. No file comes from a real device.

    python synthetic_sysdiagnose_family2.py outdir

``build_files()`` returns {relative path below the sysdiagnose folder: bytes}.
"""
import plistlib
import sys
import uuid
from datetime import datetime
from pathlib import Path

_NS = uuid.UUID('12345678-1234-5678-1234-567812345678')


def _uid(label):
    return str(uuid.uuid5(_NS, label)).upper()


SWCUTIL = '''PID:                  320
Storage:              /private/var/mobile/Containers/Data/InternalDaemon/{uid}/com.apple.SharedWebCredentials/swc.db
Settings Generation:  {{ 320, 911, 1 }}
LS Generation:        1332
Enterprise SHA:       (null)
Developer Mode:       no

=================================== DATABASE ===================================
Service:              applinks
App ID:               ABCDE12345.com.example.shop
App Version:          7.55
App PI:               <LSPersistentIdentifier 0x1> {{ v = 0 }}
Domain:               shop.example.com
Patterns:             {{"/":"/a/*"}}, {{"/":"/b/*","?":{{"x":"*"}}}}
Variables:            {{"flag":["true","false"]}}
User Approval:        unspecified
Site/Fmwk Approval:   approved
Flags:
Last Checked:         2026-08-27 22:16:23 +0000
Next Check:           2026-10-04 17:26:15 +0000
Error:                Error Domain=SWCErrorDomain Code=7 "SWCERR00101 Bad HTTP Response: 404 Not Found"
Retries:              15
--------------------------------------------------------------------------------
Service:              webcredentials
App ID:               ABCDE12345.com.example.shop
App Version:          7.55
App PI:               <LSPersistentIdentifier 0x1> {{ v = 0 }}
Domain:               *.example.com
User Approval:        unspecified
Site/Fmwk Approval:   denied
Flags:                systemApplication, alwaysEnabled
Last Checked:         2026-08-27 22:16:23 +0000
Next Check:           2026-10-04 17:26:15 +0000
--------------------------------------------------------------------------------
Service:              appclips
App ID:               0000000000.com.example.clip
App Version:          1.0
App PI:               <LSPersistentIdentifier 0x2> {{ v = 0 }}
Domain:               (null)
User Approval:        unspecified
Site/Fmwk Approval:   unspecified
Flags:                readFromDisk
--------------------------------------------------------------------------------

=================================== NETWORK ====================================


=================================== SETTINGS ===================================
{{ s = applinks, a = ABCDE12345.com.example.shop, d = (null) }}: {{
    "com.apple.LaunchServices.enabled" = 1;
}}
--------------------------------------------------------------------------------
{{ s = applinks, a = 0000000000.com.example.other, d = (null) }}: {{
    "com.apple.LaunchServices.enabled" = 0;
}}
--------------------------------------------------------------------------------
=============================== MEMORY USAGE ===============================
ignored text
'''

BRCTL_LIST = '''listing 3 containers for account {acct}:
  id:com.example.Notes localizedName:'Example Notes' documents:'/private/var/mobile/Library/Mobile Documents/com~example~Notes/Documents' [Private: inInitialState] clients: com.example.Notes
  id:iCloud.com.example.Chat localizedName:'Example Chat' documents:'/private/var/mobile/Library/Mobile Documents/iCloud~com~example~Chat/Documents' [Public:] clients: com.example.Chat, com.example.ChatWidget
  id:iCloud.com.example.Chap localizedName:'Example Chap' documents:'/private/var/mobile/Library/Mobile Documents/iCloud~com~example~Chap/Documents' [Private:] clients:
'''

# c{3}e.Notes style shortening: "{n}" replaces n hidden characters.
BRCTL_DUMP = '''brctl: dumping
    containers:   <all>
    from:         iPhone
dump taken at 2026-03-02 09:00:00.000-0500 [account=1] [inCarry=No] [home=/private/var/mobile]

database version: 34103
database ID: {dbid}
fsType: FPFS

boot_history (startup 74007.9s ago)
-----------------------------------------------------
server_truth
  [2026-08-13 08:18:38.000] OS:23G71 CloudDocs:4479.160.12 BirdSchema:34103 DBSchema:34103 DeviceID:10001
  [2026-07-20 23:19:22.000] OS:23F84 CloudDocs:4479.122.1 BirdSchema:34103 DBSchema:34103 DeviceID:10001
client_truth
  [2026-08-13 08:18:39.000] OS:23G71 CloudDocs:4479.160.12 BirdSchema:34103 DBSchema:34103 DeviceID:10001
backup_detector
  [10002|10003|1] OS:23G71 CloudDocs:4479.160.12 DBSchema:34103

server_state
-----------------------------------------------------
last-sync:2026-02-27 11:52:31.324 nextRank:901

client_state
-----------------------------------------------------
{{
    availableQuota = 0;
}}

users:

system
-----------------------------------------------------
    + network: online
    + disk:    healthy (APFS)
    + device name:   E{{13}}e

scheduler
-----------------------------------------------------
    + items:                 client:559 , server: 494
    + push environment:      production
    + push token:            {{length = 32, bytes = 0xdeadbeef}}
    + sync status:           itemsNeedUpload|nonIdleItems

-----------------------------------------------------
- <c{{1}}m.e{{5}}e.N{{3}}s[52] \x1b[0;1;32mforeground\x1b[0m {{client:idle server:full-sync|fetched-recents sync:oob-sync-ack last-sync:2026-09-17 11:52:13.478, caught-up appuninstalled:(null)}}>
-----------------------------------------------------
    + uploads:  not dumping
-----------------------------------------------------
- <i{{4}}d.c{{1}}m.e{{5}}e.C{{2}}t[70] \x1b[0;1;30mbackground\x1b[0m {{client:\x1b[0;1mblocked-app-uninstalled\x1b[0m server:fetched-recents sync:oob-sync-ack last-sync:2026-07-07 14:32:14.224, consistent appuninstalled:2026-09-20 17:45:02}}>
\x1b[0;1;34m>>> SYNC DISABLED (app not installed)\x1b[0m
-----------------------------------------------------
- <i{{4}}d.c{{1}}m.e{{5}}e.C{{2}}p[70] background {{client:idle server:idle sync:oob-sync-ack last-sync:2026-07-08 10:00:00.000, consistent appuninstalled:(null)}}>
-----------------------------------------------------
- <z{{3}}.u{{1}}.n{{3}}t[40] background {{client:idle server:idle sync:x last-sync:2026-07-08 10:00:00.000 appuninstalled:(null)}}>
-----------------------------------------------------
3 containers matching '*'
'''

TASKINFO = '''num tasks: 3

process: "launchd" [1]
unique ID/version: 1 / 1
executable uuid: {u1}
architecture: arm64e
platform: ios (2)
virtual bytes: 426.65 GiB; phys_footprint bytes: 17.06 MiB; phys_footprint lifetime maximum bytes: 17.34 MiB
run time: 42953 s
CPU time: 107.024394 s (123.70G cycles)
bytes read: 190.46 MiB written: 3.24 GiB logical writes: 262.98 MiB
runningboard managed: NO
pid suspended: NO
	req apptype: TASK_APPTYPE_NONE

process: "ExampleApp" [412]
executable uuid: {u2}
architecture: arm64
platform: ios (2)
virtual bytes: 1.5 GiB; phys_footprint bytes: 120.00 MiB; phys_footprint lifetime maximum bytes: 200.50 MiB
run time: 90 s
CPU time: 3.5 s (1.0G cycles)
bytes read: 1.00 MiB written: 5.00 KiB logical writes: 0 bytes
runningboard managed: YES
pid suspended: YES

process: "no_fields" [999]
'''


def _dt(*args):
    return datetime(*args)


def mc_settings_events():
    event = lambda name, proc, when: {'event': name, 'process': proc, 'timestamp': when}  # noqa: E731
    root = {
        'EffectiveSettings': {'intersection': {}, 'restrictedBool': {'allowThing': {'preference': event(
            'set', 'com.example.migrator', _dt(2026, 1, 2, 3, 4, 5))}}},
        'Restrictions': {'restrictedBool': {
            'allowDictation': {'value': event('remove', 'com.example.springboard', _dt(2026, 4, 8, 2, 19, 27))},
            'allowOther': {'value': event('set', 'com.example.prefs', _dt(2025, 8, 19, 16, 53, 58)),
                           'ask': event('set', 'com.example.setup', _dt(2024, 6, 14, 20, 58, 38))}}},
        'SystemClientRestrictions': {'com.example.client': {'clientRestrictions': {'union': {'ids': {
            'values': event('set', 'com.example.migrator', _dt(2024, 9, 2, 7, 44, 28))}}}}},
        'SystemProfileRestrictions': {'com.example.profile': {'intersection': {}, 'union': {}}},
        'NoiseList': [{'event': 'set', 'process': 'com.example.listed', 'timestamp': _dt(2023, 5, 6, 7, 8, 9)}],
        'BadTimestamp': {'x': {'event': 'set', 'process': 'p', 'timestamp': 'not a date'}},
    }
    return plistlib.dumps(root, fmt=plistlib.PlistFormat.FMT_BINARY)


def mc_profile_events():
    root = {'ProfileEvents': [
        {'com.example.profile-A': {'Operation': 'install', 'Process': 'com.example.prefs',
                                   'Timestamp': _dt(2026, 9, 20, 15, 56, 48)}},
        {'com.example.profile-A': {'Operation': 'remove', 'Process': 'com.example.dmd',
                                   'Timestamp': _dt(2026, 9, 20, 16, 1, 36)}},
        'not a dict', {'com.example.broken': 'text'}]}
    return plistlib.dumps(root, fmt=plistlib.PlistFormat.FMT_BINARY)


def networkextension():
    """An NSKeyedArchiver archive with two configurations, one holding a VPN-style settings dict."""
    objects = ['$null']

    def add(value):
        if value is None:
            return 0
        if isinstance(value, dict) and '$classname' in value:
            objects.append(value)
            return len(objects) - 1
        if isinstance(value, dict):
            objects.append(None)
            index = len(objects) - 1
            keys = [add(k) for k in value]
            vals = [add(v) for v in value.values()]
            klass = add({'$classname': 'NSDictionary', '$classes': ['NSDictionary', 'NSObject']})
            objects[index] = {'NS.keys': [plistlib.UID(k) for k in keys],
                              'NS.objects': [plistlib.UID(v) for v in vals], '$class': plistlib.UID(klass)}
            return index
        if isinstance(value, list):
            objects.append(None)
            index = len(objects) - 1
            items = [add(v) for v in value]
            klass = add({'$classname': 'NSArray', '$classes': ['NSArray', 'NSObject']})
            objects[index] = {'NS.objects': [plistlib.UID(i) for i in items], '$class': plistlib.UID(klass)}
            return index
        objects.append(value)
        return len(objects) - 1

    def rule(identifier, cellular, wifi, multicast=False):
        return {'SigningIdentifier': identifier, 'CellularBehavior': cellular, 'WiFiBehavior': wifi,
                'DenyAll': False, 'DenyCellularFallback': False, 'DenyMulticast': multicast,
                'NoDivertDNS': False}

    id_a, id_b = _uid('ne-a'), _uid('ne-b')
    config_a = {'Name': 'com.example.cellularusage', 'Identifier': id_a, 'Grade': 2, 'Application': '',
                'ApplicationName': '', 'VPN': '', 'ContentFilter': '',
                'PathController': {'Enabled': True, 'Rules': (
                    [rule(f'com.example.app{i}', 2, 2) for i in range(30)] + [rule('com.example.special', 0, 2)])}}
    config_b = {'Name': 'com.example.tunnel', 'Identifier': id_b, 'Grade': 1,
                'Application': 'com.example.vpnapp', 'ApplicationName': 'Example VPN',
                'VPN': {'Type': 'example', 'ServerAddress': 'vpn.example.com', 'Blob': b'\x00\x01\x02'},
                'ContentFilter': '', 'PathController': {'Enabled': False, 'Rules': []}}
    top = {id_a: add(config_a), id_b: add(config_b), 'Version': add(1), 'Generation': add(7)}
    root = {'$archiver': 'NSKeyedArchiver', '$version': 100000, '$objects': objects,
            '$top': {key: plistlib.UID(value) for key, value in top.items()}}
    return plistlib.dumps(root, fmt=plistlib.PlistFormat.FMT_BINARY)


def build_files():
    return {
        'swcutil_show.txt': SWCUTIL.format(uid=_uid('swc')).encode(),
        'brctl/brctl-container-list.txt': BRCTL_LIST.format(acct=_uid('acct')).encode(),
        'brctl/brctl-dump.txt': BRCTL_DUMP.format(dbid=_uid('db')).encode(),
        'taskinfo.txt': TASKINFO.format(u1=_uid('u1'), u2=_uid('u2')).encode(),
        'logs/MCState/Shared/MCSettingsEvents.plist': mc_settings_events(),
        'logs/MCState/Shared/MCProfileEvents.plist': mc_profile_events(),
        'logs/Networking/com.apple.networkextension.plist': networkextension(),
    }


if __name__ == '__main__':
    out = Path(sys.argv[1])
    for name, data in build_files().items():
        target = out / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
