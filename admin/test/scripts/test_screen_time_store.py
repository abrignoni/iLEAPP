"""screenTimeStore: remotemanagementd RMAdminStore databases, SYNTHETIC input only."""
import importlib.util
import json
import shutil
import sqlite3
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from scripts.artifacts import screenTimeStore as module

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('synthetic_screen_time_store', HERE / 'synthetic_screen_time_store.py')
SYNTH = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SYNTH)


def _context(files):
    return SimpleNamespace(get_files_found=lambda: [str(path) for path in files],
                           get_relative_path=lambda value: Path(value).name)


def _run(function, files):
    return function.__wrapped__(_context(files))


def _stores(folder, variant, edit=None):
    """Write the Local and Cloud synthetic stores below folder; edit(db, store) may change them first."""
    paths = []
    for store in ('Local', 'Cloud'):
        path = Path(folder) / f'RMAdminStore-{store}.sqlite'
        SYNTH.build_store(path, variant, store)
        if edit:
            db = sqlite3.connect(path)
            edit(db, store)
            db.commit()
            db.close()
        paths.append(path)
    return paths


def _count(path, query):
    db = sqlite3.connect(path)
    try:
        return db.execute(query).fetchone()[0]
    finally:
        db.close()


class ScreenTimeStoreTest(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.folder, True)

    def _child(self, edit=None):
        return _stores(self.folder, 'child', edit)

    def test_row_counts_match_an_independent_count(self):
        paths = self._child()
        local = paths[0]
        expectations = {
            module.screenTimeStoreSettings: _count(local, 'SELECT COUNT(*) FROM ZSCREENTIMESETTINGS'),
            module.screenTimeStoreOrgSettings: _count(local, 'SELECT COUNT(*) FROM ZCOREORGANIZATIONSETTINGS'),
            module.screenTimeStoreUsers: _count(local, 'SELECT COUNT(*) FROM ZUSERDEVICESTATE'),
            module.screenTimeStoreBlueprints: _count(
                local, 'SELECT COUNT(*) FROM ZBLUEPRINT b LEFT JOIN ZBLUEPRINTCONFIGURATION c ON c.ZBLUEPRINT = b.Z_PK'),
            module.screenTimeStoreInstalledApps: _count(local, 'SELECT COUNT(*) FROM ZINSTALLEDAPP'),
            module.screenTimeStoreChanges: _count(local, 'SELECT COUNT(*) FROM ATRANSACTION'),
            module.screenTimeStoreDeletedRows: _count(local, 'SELECT COUNT(*) FROM ACHANGE WHERE ZCHANGETYPE = 2'),
        }
        usage = sum(_count(p, query) for p in paths for query in (
            'SELECT COUNT(*) FROM ZUSAGECATEGORY x JOIN ZUSAGEBLOCK b ON b.Z_PK = x.ZBLOCK',
            'SELECT COUNT(*) FROM ZUSAGETIMEDITEM x JOIN ZUSAGECATEGORY c ON c.Z_PK = x.ZCATEGORY '
            'JOIN ZUSAGEBLOCK b ON b.Z_PK = c.ZBLOCK',
            'SELECT COUNT(*) FROM ZUSAGECOUNTEDITEM x JOIN ZUSAGEBLOCK b ON b.Z_PK = x.ZBLOCK'))
        expectations[module.screenTimeStoreUsage] = usage
        for function, expected in expectations.items():
            headers, rows, source = _run(function, paths)
            self.assertEqual(len(rows), expected, function.__name__)
            self.assertTrue(all(len(row) == len(headers) for row in rows), function.__name__)
            self.assertIn('RMAdminStore-Local.sqlite', source)
        self.assertEqual(usage, 7)           # local: 2 category, 2 timed, 1 counted; cloud: 1 category, 1 timed

    def test_users_join_and_a_state_row_with_no_user_or_device(self):
        headers, rows, _ = _run(module.screenTimeStoreUsers, self._child())
        column = {name[0] if isinstance(name, tuple) else name: i for i, name in enumerate(headers)}
        first, orphan = rows[0], rows[1]
        self.assertEqual(first[column['Apple Account']], 'child.example@example.invalid')
        self.assertEqual(first[column['Device Name']], 'Example iPhone')
        self.assertEqual(first[column['Family Member Type']], 'Child')
        self.assertEqual(first[column['Management Enabled']], 'Yes')
        self.assertEqual(first[column['Last Passcode Use']].isoformat(), '2026-05-11T06:13:20+00:00')
        self.assertEqual((orphan[column['Apple Account']], orphan[column['Device Name']]), (None, None))
        self.assertEqual(orphan[column['Screen Time Enabled']], '')       # NULL stays blank, not 'No'

    def test_passcode_value_is_never_copied(self):
        paths = self._child()
        headers, rows, _ = _run(module.screenTimeStoreOrgSettings, paths)
        self.assertNotIn('synthetic-secret', repr(rows))
        self.assertEqual(rows[0][headers.index('Passcode Stored')], 'Yes')
        plain = _stores(tempfile.mkdtemp(dir=self.folder), 'plain')
        headers, rows, _ = _run(module.screenTimeStoreOrgSettings, plain)
        self.assertEqual(rows[0][headers.index('Passcode Stored')], 'No')

    def test_flags_integers_and_null_are_kept_apart(self):
        headers, rows, _ = _run(module.screenTimeStoreOrgSettings, self._child())
        row = rows[0]
        self.assertEqual(row[headers.index('All Limits Enabled')], 'Yes')
        self.assertEqual(row[headers.index('Communication Policy')], 2)          # integer as stored
        self.assertEqual(row[headers.index('Contact Management State')], None)    # NULL integer
        self.assertEqual(row[headers.index('Communication Safety Analytics')], 'No')
        self.assertEqual(row[headers.index('Communication Safety Sending Restricted')], '')
        self.assertEqual(row[headers.index('App And Website Activity')], 'Yes')   # second column used
        headers, rows, _ = _run(module.screenTimeStoreSettings, self._child())
        self.assertEqual(rows[0][headers.index('Row Version')], 40)

    def test_declarations_are_decoded_and_a_bad_payload_is_reported(self):
        headers, rows, _ = _run(module.screenTimeStoreBlueprints, self._child())
        by_config = {row[headers.index('Configuration Identifier')]: row for row in rows}
        apps = by_config['always_allow_app_configuration_personal']
        self.assertEqual(apps[headers.index('Declaration Type')], 'com.apple.configuration.policy.application')
        self.assertEqual(json.loads(apps[headers.index('Payload')]),
                         {'Apps': ['com.example.phone', 'com.example.messages'], 'Mode': 'Override'})
        store = by_config['digital_health_restrictions.application.store']
        payload = json.loads(store[headers.index('Payload')])
        self.assertEqual(payload['checked'], '2026-05-10T12:00:00')
        self.assertEqual(payload['token'], '010203')
        self.assertEqual(payload['allowAppInstallation'], False)
        self.assertEqual(store[headers.index('Enabled')], 'No')                 # shown, not claimed in force
        broken = by_config['broken_configuration']
        self.assertEqual(broken[headers.index('Declaration Type')], '')
        self.assertEqual(broken[headers.index('Payload')], 'undecodable (19 bytes)')
        bare = [r for r in rows if r[headers.index('Blueprint Identifier')] == 'managed_user_activation_0']
        self.assertEqual(len(bare), 1)
        self.assertEqual(bare[0][headers.index('Configuration Identifier')], '')
        self.assertEqual(bare[0][headers.index('Tombstoned')], 'Yes')

    def test_usage_rows_carry_each_kind_and_both_stores(self):
        headers, rows, _ = _run(module.screenTimeStoreUsage, self._child())
        column = {name[0] if isinstance(name, tuple) else name: i for i, name in enumerate(headers)}
        kinds = {}
        for row in rows:
            kinds.setdefault(row[column['Kind']], []).append(row)
        self.assertEqual({k: len(v) for k, v in kinds.items()}, {'Category': 3, 'Timed item': 3, 'Counted item': 1})
        counted = kinds['Counted item'][0]
        self.assertEqual((counted[column['Pickups']], counted[column['Notifications']]), (2, 4))
        web = next(r for r in kinds['Timed item'] if r[column['Web Domain']])
        self.assertEqual((web[column['Web Domain']], web[column['Bundle Identifier']], web[column['Usage Trusted']]),
                         ('www.example.invalid', '', 'No'))
        self.assertEqual({r[column['Store']] for r in rows}, {'Local', 'Cloud'})
        starts = [r[0] for r in rows]
        self.assertEqual(starts, sorted(starts))
        category = kinds['Category'][0]
        self.assertEqual((category[column['Category']], category[column['Seconds']]), ('SYNTH-CAT-SOCIAL', 600))

    def test_history_counts_authors_and_entities(self):
        headers, rows, _ = _run(module.screenTimeStoreChanges, self._child())
        column = {name[0] if isinstance(name, tuple) else name: i for i, name in enumerate(headers)}
        self.assertEqual(len(rows), 3)
        first, second, third = rows
        self.assertEqual((first[column['Author']], first[column['Bundle ID']], first[column['Process (as stored)']]),
                         ('ExampleOperation', 'com.example.settingsagent', 'SettingsAgent'))
        self.assertEqual((first[column['Inserts']], first[column['Updates']], first[column['Deletes']]), (1, 0, 0))
        self.assertEqual(first[column['Entities']], 'Blueprint')
        self.assertEqual((second[column['Inserts']], second[column['Updates']], second[column['Deletes']]), (0, 3, 1))
        self.assertEqual(second[column['Author']], '')
        self.assertEqual(second[column['Entities']], 'Blueprint, CoreUser, ScreenTimeSettings')
        self.assertEqual(third[column['Entities']], 'entity 99')           # an entity id the store does not name
        self.assertEqual([r[0] for r in rows], sorted(r[0] for r in rows))

    def test_deleted_rows_keep_tombstones_as_stored(self):
        def edit(db, store):
            if store == 'Local':
                db.execute("UPDATE ACHANGE SET ZTOMBSTONE0 = 'com.example.removed', ZTOMBSTONE1 = 7, "
                           "ZTOMBSTONE2 = X'0A0B', ZTOMBSTONE3 = 'app:com.example.removed-uds:1:SYNTH' "
                           "WHERE Z_PK = 4")
        headers, rows, _ = _run(module.screenTimeStoreDeletedRows, self._child(edit))
        column = {name[0] if isinstance(name, tuple) else name: i for i, name in enumerate(headers)}
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row[column['Entity']], 'Blueprint')
        self.assertEqual([row[column[f'Value {i} (as stored)']] for i in (1, 2, 3, 4)],
                         ['com.example.removed', 7, '0a0b', 'app:com.example.removed-uds:1:SYNTH'])
        self.assertEqual(row[column['Bundle ID']], 'com.example.prefs')
        # the same delete with no tombstone values leaves the value columns blank
        _, rows, _ = _run(module.screenTimeStoreDeletedRows, self._child())
        self.assertEqual([rows[0][column[f'Value {i} (as stored)']] for i in (1, 2, 3, 4)], ['', '', '', ''])

    def test_older_store_without_some_columns_still_reads(self):
        def edit(db, _store):
            SYNTH.trim_columns(db, 'ZCOREORGANIZATIONSETTINGS',
                               ['ZISEYERELIEFENABLED', 'ZISAPPANDWEBSITEACTIVITYENABLED1', 'ZPASSCODE1', 'ZPASSCODE2'])
            SYNTH.trim_columns(db, 'ZUSERDEVICESTATE', ['ZLASTFAMILYCHECKINDATE', 'ZISLEGACYUSAGEDISABLED'])
        paths = self._child(edit)
        headers, rows, _ = _run(module.screenTimeStoreOrgSettings, paths)
        self.assertEqual(len(rows), 1)                       # the cloud store of this variant has no organization row
        local = rows[0]
        self.assertEqual(local[headers.index('Eye Relief Enabled')], '')
        self.assertEqual(local[headers.index('App And Website Activity')], '')
        self.assertEqual(local[headers.index('Passcode Stored')], 'Yes')
        headers, rows, _ = _run(module.screenTimeStoreUsers, paths)
        self.assertEqual(rows[0][headers.index('Legacy Usage Disabled')], '')

    def test_store_without_a_table_gives_no_rows_for_that_artifact(self):
        def edit(db, _store):
            db.execute('DROP TABLE ZINSTALLEDAPP')
            db.execute('DROP TABLE ACHANGE')
        paths = self._child(edit)
        self.assertEqual(_run(module.screenTimeStoreInstalledApps, paths)[1], [])
        self.assertEqual(_run(module.screenTimeStoreDeletedRows, paths)[1], [])
        self.assertEqual(len(_run(module.screenTimeStoreChanges, paths)[1]), 3)   # transactions still listed

    def test_cloud_only_and_sidecar_files(self):
        paths = self._child()
        extra = []
        for path in paths:
            for suffix in ('-wal', '-shm'):
                sidecar = Path(str(path) + suffix)
                sidecar.write_bytes(b'')
                extra.append(sidecar)
        cloud_only = [paths[1]] + extra
        headers, rows, source = _run(module.screenTimeStoreUsage, cloud_only)
        self.assertEqual(len(rows), 2)           # the cloud store's category row and timed item
        self.assertEqual({row[headers.index('Store')] for row in rows}, {'Cloud'})
        self.assertEqual(source.count('RMAdminStore-'), 1)

    def test_plain_store_reads_as_the_unmanaged_shape(self):
        paths = _stores(self.folder, 'plain')
        _, rows, _ = _run(module.screenTimeStoreUsage, paths)
        self.assertEqual(rows, [])
        _, rows, _ = _run(module.screenTimeStoreInstalledApps, paths)
        self.assertEqual(rows, [])
        headers, rows, _ = _run(module.screenTimeStoreUsers, paths)
        self.assertEqual(rows[0][headers.index('Family Member Type')], 'Unknown')
        headers, rows, _ = _run(module.screenTimeStoreSettings, paths)
        self.assertEqual([rows[0][headers.index(h)] for h in
                          ('Screen Time Enabled', 'Cloud Sync Enabled', 'Family Setup Complete')], ['No', 'No', ''])


if __name__ == '__main__':
    unittest.main()
