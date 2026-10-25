"""swcutil, MCState events, Network Extension, brctl and taskinfo sysdiagnose artifacts.

SYNTHETIC input only: the files come from synthetic_sysdiagnose_family2.py.
"""
import importlib.util
import tarfile
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from scripts.artifacts import sdl_brctl, sdl_mc_events, sdl_network_extension, sdl_swcutil, sdl_taskinfo

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('synthetic_sysdiagnose_family2', HERE / 'synthetic_sysdiagnose_family2.py')
SYNTH = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SYNTH)

FOLDER = 'sysdiagnose_SYNTHETIC_iPhone-OS_iPhone_00A000'


def _context(paths):
    return SimpleNamespace(get_files_found=lambda: [str(p) for p in paths],
                           get_relative_path=lambda value: value.replace('\\', '/').split('/')[-1]
                           if ' >> ' not in value else value.split(' >> ')[0].replace('\\', '/').split('/')[-1]
                           + ' >> ' + value.split(' >> ')[1])


def _run(function, paths):
    headers, rows, source = function.__wrapped__(_context(paths))
    names = [h[0] if isinstance(h, tuple) else h for h in headers]
    return [dict(zip(names, row)) for row in rows], source


class FolderTest(unittest.TestCase):
    """Files laid out as an extracted sysdiagnose folder."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / FOLDER
        self.files = SYNTH.build_files()
        self.paths = {}
        for name, data in self.files.items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            self.paths[name] = path

    def tearDown(self):
        self.tmp.cleanup()

    def test_swcutil_domains(self):
        rows, _ = _run(sdl_swcutil.swcutil_associated_domains, [self.paths['swcutil_show.txt']])
        self.assertEqual(len(rows), 3)
        self.assertEqual(sum(1 for line in self.files['swcutil_show.txt'].decode().splitlines()
                             if line.startswith('Service:')), 3)
        first, second, third = rows
        self.assertEqual((first['Service'], first['App ID'], first['Domain']),
                         ('applinks', 'ABCDE12345.com.example.shop', 'shop.example.com'))
        self.assertEqual(first['Retries'], '15')
        self.assertTrue(first['Error'].startswith('Error Domain=SWCErrorDomain'))
        self.assertEqual((first['Pattern Entries'], first['Variable Entries']), (2, 1))
        self.assertEqual(str(first['Last Checked']), '2026-08-27 22:16:23+00:00')
        self.assertEqual(second['Site/Framework Approval'], 'denied')
        self.assertEqual(second['Flags'], 'systemApplication, alwaysEnabled')
        self.assertEqual(third['Domain'], '')
        self.assertEqual(third['Last Checked'], '')

    def test_swcutil_settings(self):
        rows, _ = _run(sdl_swcutil.swcutil_settings, [self.paths['swcutil_show.txt']])
        self.assertEqual([(r['App ID'], r['Setting'], r['Value']) for r in rows], [
            ('ABCDE12345.com.example.shop', 'com.apple.LaunchServices.enabled', '1'),
            ('0000000000.com.example.other', 'com.apple.LaunchServices.enabled', '0')])

    def test_mc_settings_events(self):
        rows, _ = _run(sdl_mc_events.mc_settings_events,
                       [self.paths['logs/MCState/Shared/MCSettingsEvents.plist']])
        paths = {(r['Section'], r['Path']): r for r in rows}
        # five event dictionaries inside dicts plus one inside a list; the bad timestamp keeps its row
        self.assertEqual(len(rows), 7)
        removed = paths[('Restrictions', 'restrictedBool > allowDictation > value')]
        self.assertEqual((removed['Event'], removed['Process']), ('remove', 'com.example.springboard'))
        self.assertEqual(str(removed['Timestamp']), '2026-04-08 02:19:27+00:00')
        self.assertIn(('Restrictions', 'restrictedBool > allowOther > ask'), paths)
        self.assertIn(('SystemClientRestrictions', 'com.example.client > clientRestrictions > union > ids > values'),
                      paths)
        self.assertEqual(paths[('NoiseList', '0')]['Process'], 'com.example.listed')
        self.assertEqual(paths[('BadTimestamp', 'x')]['Timestamp'], '')
        self.assertEqual([r['Timestamp'] for r in rows if r['Timestamp']],
                         sorted(r['Timestamp'] for r in rows if r['Timestamp']))

    def test_mc_profile_events(self):
        rows, _ = _run(sdl_mc_events.mc_profile_events,
                       [self.paths['logs/MCState/Shared/MCProfileEvents.plist']])
        self.assertEqual([(r['Operation'], r['Process']) for r in rows],
                         [('install', 'com.example.prefs'), ('remove', 'com.example.dmd')])
        self.assertEqual(rows[0]['Profile Identifier'], 'com.example.profile-A')

    def test_network_extension(self):
        path = self.paths['logs/Networking/com.apple.networkextension.plist']
        rows, _ = _run(sdl_network_extension.ne_configurations, [path])
        self.assertEqual(len(rows), 2)
        plain = {r['Name']: r for r in rows}
        cellular = plain['com.example.cellularusage']
        self.assertEqual((cellular['Service Types'], cellular['Path Rule Count'], cellular['Path Rules Enabled']),
                         ('', 31, 'True'))
        tunnel = plain['com.example.tunnel']
        self.assertEqual(tunnel['Service Types'], 'VPN')
        self.assertEqual(tunnel['Application Name'], 'Example VPN')
        self.assertIn('"ServerAddress": "vpn.example.com"', tunnel['Service Settings'])
        self.assertIn('<3 bytes>', tunnel['Service Settings'])
        groups, _ = _run(sdl_network_extension.ne_path_rules, [path])
        self.assertEqual([(g['Rule Count'], g['Cellular Behavior (as stored)']) for g in groups],
                         [(30, '2'), (1, '0')])
        self.assertEqual(groups[0]['Signing Identifiers'], '')   # more than 25 rules: members not listed
        self.assertEqual(groups[1]['Signing Identifiers'], 'com.example.special')

    def test_brctl(self):
        paths = [self.paths['brctl/brctl-container-list.txt'], self.paths['brctl/brctl-dump.txt']]
        rows, _ = _run(sdl_brctl.brctl_containers, paths)
        self.assertEqual(len(rows), 4)
        by_id = {r['Container ID']: r for r in rows}
        notes = by_id['com.example.Notes']
        self.assertEqual((notes['Dump Match'], notes['Library Mode'], notes['Client State']),
                         ('Yes', 'foreground', 'idle'))
        self.assertEqual(notes['Scope'], 'Private: inInitialState')
        chat = by_id['iCloud.com.example.Chat']
        self.assertEqual((chat['Client State'], chat['App Uninstalled']), ('blocked-app-uninstalled', '2026-09-20 17:45:02'))
        self.assertEqual(chat['Clients'], 'com.example.Chat, com.example.ChatWidget')
        self.assertEqual(by_id['iCloud.com.example.Chap']['Dump Match'], 'Yes')
        self.assertEqual(by_id['iCloud.com.example.Chap']['Clients'], '')
        dump_only = [r for r in rows if r['Dump Match'] == 'Dump only']
        self.assertEqual(len(dump_only), 1)
        self.assertEqual(dump_only[0]['Container ID'], 'z{3}.u{1}.n{3}t')
        # the list alone still gives the containers
        rows_alone, _ = _run(sdl_brctl.brctl_containers, [self.paths['brctl/brctl-container-list.txt']])
        self.assertEqual(len(rows_alone), 3)
        self.assertEqual({r['Dump Match'] for r in rows_alone}, {''})

    def test_brctl_history_and_state(self):
        path = self.paths['brctl/brctl-dump.txt']
        rows, _ = _run(sdl_brctl.brctl_boot_history, [path])
        self.assertEqual([(r['List'], r['OS Build']) for r in rows], [
            ('server_truth', '23G71'), ('server_truth', '23F84'), ('client_truth', '23G71'),
            ('backup_detector', '23G71')])
        self.assertEqual(rows[0]['Time (as printed)'], '2026-08-13 08:18:38.000')
        self.assertEqual(rows[3]['Time (as printed)'], '')
        state, _ = _run(sdl_brctl.brctl_state, [path])
        pairs = {(r['Block'], r['Key']): r['Value'] for r in state}
        self.assertEqual(pairs[('header', 'dump taken at')], '2026-03-02 09:00:00.000-0500 [account=1] [inCarry=No] [home=/private/var/mobile]')
        self.assertEqual(pairs[('system', 'network')], 'online')
        self.assertEqual(pairs[('scheduler', 'push environment')], 'production')
        self.assertNotIn(('scheduler', 'push token'), pairs)

    def test_taskinfo(self):
        rows, _ = _run(sdl_taskinfo.taskinfo_processes, [self.paths['taskinfo.txt']])
        self.assertEqual([r['Process'] for r in rows], ['launchd', 'ExampleApp', 'no_fields'])
        launchd, app, empty = rows
        self.assertEqual((launchd['PID'], launchd['Run Time (s)'], launchd['CPU Time (s)']), (1, 42953, 107.024394))
        self.assertEqual((launchd['Physical Footprint'], launchd['Lifetime Maximum Footprint']),
                         ('17.06 MiB', '17.34 MiB'))
        self.assertEqual((launchd['Bytes Read'], launchd['Bytes Written']), ('190.46 MiB', '3.24 GiB'))
        self.assertEqual((app['RunningBoard Managed'], app['PID Suspended'], app['Architecture']),
                         ('YES', 'YES', 'arm64'))
        self.assertEqual((empty['Run Time (s)'], empty['Executable UUID']), ('', ''))

    def test_brctl_history_older_time_form(self):
        # the iOS 13 and 14 dumps print a 12-hour M/DD/YY time and no DeviceID
        older = Path(self.tmp.name) / 'older_brctl' / 'brctl-dump.txt'
        older.parent.mkdir()
        older.write_text('boot_history (version 1.0 a)\n---\nserver_truth\n'
                         '  [2/19/21, 4:10:01 PM] OS:18C66 CloudDocs:100 BirdSchema:20000 DBSchema:20000\n'
                         'client_truth\n'
                         '  [2/18/21, 9:00:00 AM] OS:18B92 CloudDocs:100 BirdSchema:20000 DBSchema:20000\n'
                         'server_state\n', encoding='utf-8')
        rows, _ = _run(sdl_brctl.brctl_boot_history, [str(older)])
        self.assertEqual([(r['List'], r['Time (as printed)'], r['OS Build']) for r in rows],
                         [('server_truth', '2/19/21, 4:10:01 PM', '18C66'),
                          ('client_truth', '2/18/21, 9:00:00 AM', '18B92')])

    def test_taskinfo_older_process_line(self):
        # iOS 14 and 17 print '[unique ID: N]' after the PID
        older = Path(self.tmp.name) / 'older' / 'taskinfo.txt'
        older.parent.mkdir()
        older.write_text('num tasks: 1\n\nprocess: "launchd" [1] [unique ID: 1]\n'
                         'architecture: arm64e\nrun time: 42 s\npid suspended: NO\n',
                         encoding='utf-8')
        rows, _ = _run(sdl_taskinfo.taskinfo_processes, [str(older)])
        self.assertEqual([(r['Process'], r['PID'], r['Run Time (s)']) for r in rows], [('launchd', 1, 42)])


class ArchiveTest(unittest.TestCase):
    def test_files_read_from_a_sysdiagnose_archive(self):
        with tempfile.TemporaryDirectory() as folder:
            archive = Path(folder) / f'{FOLDER}.tar.gz'
            with tarfile.open(archive, 'w:gz') as tar:
                for name, data in SYNTH.build_files().items():
                    source = Path(folder) / 'member'
                    source.write_bytes(data)
                    tar.add(source, arcname=f'{FOLDER}/{name}')
                    # an AppleDouble sidecar must be ignored
                    tar.add(source, arcname=f'{FOLDER}/{Path(name).parent.as_posix()}/._{Path(name).name}')
            self.assertEqual(len(_run(sdl_swcutil.swcutil_associated_domains, [archive])[0]), 3)
            self.assertEqual(len(_run(sdl_mc_events.mc_profile_events, [archive])[0]), 2)
            self.assertEqual(len(_run(sdl_network_extension.ne_configurations, [archive])[0]), 2)
            self.assertEqual(len(_run(sdl_taskinfo.taskinfo_processes, [archive])[0]), 3)
            rows, _ = _run(sdl_brctl.brctl_containers, [archive])
            self.assertEqual(len(rows), 4)
            self.assertEqual(sum(1 for r in rows if r['Dump Match'] == 'Yes'), 3)


class DamagedInputTest(unittest.TestCase):
    def test_empty_and_garbage_files(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            names = {'swcutil_show.txt': (sdl_swcutil.swcutil_associated_domains, sdl_swcutil.swcutil_settings),
                     'MCSettingsEvents.plist': (sdl_mc_events.mc_settings_events,),
                     'MCProfileEvents.plist': (sdl_mc_events.mc_profile_events,),
                     'com.apple.networkextension.plist': (sdl_network_extension.ne_configurations,
                                                          sdl_network_extension.ne_path_rules),
                     'brctl-dump.txt': (sdl_brctl.brctl_containers, sdl_brctl.brctl_boot_history,
                                        sdl_brctl.brctl_state),
                     'brctl-container-list.txt': (sdl_brctl.brctl_containers,),
                     'taskinfo.txt': (sdl_taskinfo.taskinfo_processes,)}
            for content in (b'', b'\x00\xff garbage \xfe' * 50):
                for name, functions in names.items():
                    path = root / name
                    path.write_bytes(content)
                    for function in functions:
                        rows, _ = _run(function, [path])
                        self.assertEqual(rows, [], f'{function.__name__} {name} {content[:4]!r}')


if __name__ == '__main__':
    unittest.main()
