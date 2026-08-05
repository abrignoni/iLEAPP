#!/usr/bin/env python3
"""Opt-in structural checks against a local, non-public extraction.

Some artifacts are only present in images that cannot be committed to this
repository, so the usual route (`make_test_data.py` into
`admin/test/cases/data/`, expected output into `admin/test/results/`) is not
available: both of those record the parsed values themselves.

These tests take the other route. Point ILEAPP_LOCAL_IMAGE at an extraction and
they run the real artifact code over the real database, asserting only
structural invariants: column counts, value shapes, timestamp sanity. No value
from the image is written to disk or recorded in an assertion, so nothing about
the device enters the repository or the test output. Without the variable set
they skip, which is what happens in CI.

    ILEAPP_LOCAL_IMAGE=/path/to/extraction.zip \
        python -m pytest admin/test/scripts/test_local_corpus_artifacts.py -v

Accepts a .zip extraction or a directory of extracted files.
"""

import os
import re
import shutil
import tempfile
import unittest
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from scripts.artifacts.appleAccountDeviceList import appleAccountDeletedDeviceList, \
    appleAccountDeviceList
from scripts.artifacts.locationdCacheEncryptedB import locationdCellLocations, \
    locationdWifiHarvest, locationdWifiLocations, locationdWifiTiles
from scripts.artifacts.powerlog import powerlogApplicationRuntime, powerlogAppState, \
    powerlogAudioRouting, powerlogBatteryLevel, powerlogDeviceLock, \
    powerlogDevicePowerState, powerlogDisplayState, powerTelemetryBatteryDataDaily, \
    powerTelemetrySmartCharging
from scripts.artifacts.safariCache import safariCache
from scripts.artifacts.storeSystem import storeSystemAppInstalls, storeSystemAppPackages, \
    storeSystemAppUpdates
from scripts.artifacts.threeBars import threeBarsAccessPoints, threeBarsNetworks, \
    threeBarsTiles

LOCAL_IMAGE = os.environ.get('ILEAPP_LOCAL_IMAGE', '')

# Timestamps outside this window mean the epoch was read wrong, whatever the
# image is. Apple shipped no iOS device before 2007 and these are not future
# dated fields.
EARLIEST_PLAUSIBLE = datetime(2007, 1, 1, tzinfo=timezone.utc)
LATEST_PLAUSIBLE = datetime(2100, 1, 1, tzinfo=timezone.utc)


def _redact(value):
    """Reduce a value to its shape so failures can be reported safely."""
    return re.sub(r'\w', '#', str(value))


class _Context:
    def __init__(self, path):
        self.path = str(path)

    def get_files_found(self):
        return [self.path]

    def get_relative_path(self, path):
        return Path(path).name


class LocalCorpusTestCase(unittest.TestCase):
    """Base class handling the lookup of a file inside the local image."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)

    def fetch(self, suffix):
        """Copy the first file whose path ends with suffix out of the image.

        Returns None when the image does not carry the file, which is a skip
        rather than a failure: these images are whatever the examiner had.
        """
        destination = Path(self.temp_dir.name) / Path(suffix).name
        source = Path(LOCAL_IMAGE)

        if source.is_dir():
            for candidate in source.rglob(Path(suffix).name):
                if str(candidate).replace(os.sep, '/').endswith(suffix):
                    shutil.copy2(candidate, destination)
                    return destination
            return None

        with zipfile.ZipFile(source) as archive:
            for name in archive.namelist():
                if name.endswith(suffix):
                    with archive.open(name) as member, open(destination, 'wb') as out:
                        shutil.copyfileobj(member, out)
                    return destination
        return None

    def assert_row_shape(self, headers, rows):
        """Every row matches the declared headers."""
        for row in rows:
            self.assertEqual(len(row), len(headers))

    def assert_matches(self, value, pattern, label):
        """Assert a value's shape, reporting only the shape when it fails.

        unittest prints the compared values on failure, which would put image
        content in the test log. Everything reported here is redacted first.
        """
        self.assertTrue(
            re.match(pattern, str(value)),
            f'{label} does not match {pattern}; value shape was {_redact(value)}')

    def assert_plausible_timestamp(self, value):
        """A parsed timestamp column holds a sane datetime, or nothing at all."""
        if value in (None, ''):
            return
        self.assertIsInstance(value, datetime)
        self.assertIsNotNone(value.tzinfo)
        self.assertTrue(
            EARLIEST_PLAUSIBLE < value < LATEST_PLAUSIBLE,
            f'timestamp outside {EARLIEST_PLAUSIBLE.year}-{LATEST_PLAUSIBLE.year}; '
            f'value shape was {_redact(value)}')


@unittest.skipUnless(LOCAL_IMAGE, 'set ILEAPP_LOCAL_IMAGE to run local corpus tests')
class AppleAccountDeviceListLocalTest(LocalCorpusTestCase):
    SUFFIX = 'Library/Application Support/com.apple.akd/devicelist.db'

    def setUp(self):
        super().setUp()
        self.path = self.fetch(self.SUFFIX)
        if not self.path:
            self.skipTest(f'{self.SUFFIX} not present in {LOCAL_IMAGE}')

    def test_device_list_structure(self):
        headers, rows, source = appleAccountDeviceList.__wrapped__(_Context(self.path))
        self.assertEqual(source, str(self.path))
        self.assertTrue(rows, 'device_list parsed no rows')
        self.assert_row_shape(headers, rows)

        for row in rows:
            self.assert_plausible_timestamp(row[0])   # Last Updated
            self.assert_plausible_timestamp(row[1])   # Last Cache Updated
            self.assert_matches(row[9], r'^(Yes|No)$', 'Trusted')
            if row[8]:                                # IMEI, when the blob held one
                for imei in row[8].split(', '):
                    self.assert_matches(imei, r'^\d{14,16}$', 'IMEI')
            if row[5]:                                # OS Version
                self.assert_matches(row[5], r'^\d+(\.\d+)*$', 'OS Version')

    def test_deleted_device_list_structure(self):
        headers, rows, _ = appleAccountDeletedDeviceList.__wrapped__(_Context(self.path))
        self.assert_row_shape(headers, rows)
        for row in rows:
            self.assert_plausible_timestamp(row[0])
            self.assert_plausible_timestamp(row[1])

    def test_no_column_is_wholly_unparsed(self):
        """Catch a column that silently yields nothing on every row.

        A header that is empty in every row usually means the query names a
        column the schema does not have, or a decode step failed. Columns that
        are legitimately sparse are listed as exempt.
        """
        headers, rows, _ = appleAccountDeviceList.__wrapped__(_Context(self.path))
        exempt = {'IMEI', 'Additional Info', 'Circle Status'}
        for index, header in enumerate(headers):
            label = header[0] if isinstance(header, tuple) else header
            if label in exempt:
                continue
            populated = any(row[index] not in (None, '') for row in rows)
            self.assertTrue(populated, f'every row is empty for column {label}')


@unittest.skipUnless(LOCAL_IMAGE, 'set ILEAPP_LOCAL_IMAGE to run local corpus tests')
class StoreSystemLocalTest(LocalCorpusTestCase):
    SUFFIX = 'Documents/Persistence/storeSystem.db'

    def setUp(self):
        super().setUp()
        self.path = self.fetch(self.SUFFIX)
        if not self.path:
            self.skipTest(f'{self.SUFFIX} not present in {LOCAL_IMAGE}')

    def test_installs_structure(self):
        headers, rows, _ = storeSystemAppInstalls.__wrapped__(_Context(self.path))
        self.assert_row_shape(headers, rows)
        if not rows:
            self.skipTest('app_install is empty in this image')
        for row in rows:
            self.assert_plausible_timestamp(row[0])   # Record Timestamp
            self.assert_plausible_timestamp(row[2])   # Last Start Date
            self.assert_plausible_timestamp(row[3])   # Purchase Date
            self.assert_matches(row[6], r'^[\w.-]+$', 'Bundle ID')
            if row[12]:                               # Apple ID, when metadata carried one
                self.assert_matches(row[12], r'^[^@\s]+@[^@\s]+$', 'Apple ID')
            if row[21]:                               # Install Path
                self.assert_matches(row[21], r'^file:///.*\.app/?$', 'Install Path')

    def test_updates_structure(self):
        headers, rows, _ = storeSystemAppUpdates.__wrapped__(_Context(self.path))
        self.assert_row_shape(headers, rows)
        if not rows:
            self.skipTest('mapi_app_update is empty in this image')
        for row in rows:
            self.assert_plausible_timestamp(row[0])
            self.assert_plausible_timestamp(row[1])
            self.assert_matches(row[5], r'^[\w.-]+$', 'Bundle ID')

    def test_packages_join_resolves(self):
        """Every package should resolve to the install record that owns it."""
        headers, rows, _ = storeSystemAppPackages.__wrapped__(_Context(self.path))
        self.assert_row_shape(headers, rows)
        if not rows:
            self.skipTest('app_package is empty in this image')
        unresolved = sum(1 for row in rows if not row[1])
        self.assertEqual(unresolved, 0,
                         f'{unresolved} of {len(rows)} packages did not join to an install')
        for row in rows:
            self.assert_plausible_timestamp(row[0])
            if row[4] not in (None, ''):              # Bytes Total
                self.assertGreater(row[4], 0)


@unittest.skipUnless(LOCAL_IMAGE, 'set ILEAPP_LOCAL_IMAGE to run local corpus tests')
class SafariCacheLocalTest(LocalCorpusTestCase):
    SUFFIX = 'Library/Caches/com.apple.mobilesafari/Cache.db'

    def setUp(self):
        super().setUp()
        self.path = self.fetch(self.SUFFIX)
        if not self.path:
            self.skipTest(f'{self.SUFFIX} not present in {LOCAL_IMAGE}')
        # The WAL carries records that the database file alone does not, so a run
        # without it silently under-reports. Pull it across when the image has one.
        self.fetch(self.SUFFIX + '-wal')
        self.fetch(self.SUFFIX + '-shm')

    def test_cache_structure(self):
        headers, rows, _ = safariCache.__wrapped__(_Context(self.path))
        self.assert_row_shape(headers, rows)
        if not rows:
            self.skipTest('cfurl_cache_response is empty in this image')
        for row in rows:
            self.assert_plausible_timestamp(row[0])
            self.assert_matches(row[1], r'^\w+:', 'Request URL')
            if row[2] != '':                              # HTTP Status
                self.assertGreaterEqual(row[2], 100)
                self.assertLessEqual(row[2], 599)
            if row[4]:                                    # MIME Type
                self.assert_matches(row[4], r'^[\w.+-]+/[\w.+-]+$', 'MIME Type')
            self.assertIn(row[6], ('Database', 'File system', ''))

    def test_payload_sizes_are_consistent(self):
        """An inline payload reports the byte count actually held in the row."""
        _, rows, _ = safariCache.__wrapped__(_Context(self.path))
        if not rows:
            self.skipTest('cfurl_cache_response is empty in this image')
        inline = [row for row in rows if row[6] == 'Database']
        if not inline:
            self.skipTest('no inline payloads in this image')
        for row in inline:
            self.assertIsInstance(row[8], int)
            self.assertGreater(row[8], 0)


@unittest.skipUnless(LOCAL_IMAGE, 'set ILEAPP_LOCAL_IMAGE to run local corpus tests')
class ThreeBarsLocalTest(LocalCorpusTestCase):
    SUFFIX = 'Library/Caches/com.apple.wifid/ThreeBars.sqlite'

    def setUp(self):
        super().setUp()
        self.path = self.fetch(self.SUFFIX)
        if not self.path:
            self.skipTest(f'{self.SUFFIX} not present in {LOCAL_IMAGE}')
        self.fetch(self.SUFFIX + '-wal')
        self.fetch(self.SUFFIX + '-shm')

    def _assert_coordinates(self, rows, latitude_index, longitude_index):
        for row in rows:
            latitude, longitude = row[latitude_index], row[longitude_index]
            if latitude == '' and longitude == '':
                continue        # the blanked 0/0 placeholder
            self.assertTrue(-90 <= latitude <= 90,
                            f'latitude out of range; shape was {_redact(latitude)}')
            self.assertTrue(-180 <= longitude <= 180,
                            f'longitude out of range; shape was {_redact(longitude)}')
            self.assertFalse(latitude == 0 and longitude == 0,
                             'a 0/0 pair reached the report unblanked')

    def test_networks_structure(self):
        headers, rows, _ = threeBarsNetworks.__wrapped__(_Context(self.path))
        self.assert_row_shape(headers, rows)
        if not rows:
            self.skipTest('ZNETWORK is empty in this image')
        self._assert_coordinates(rows, 1, 2)
        for row in rows:
            self.assert_plausible_timestamp(row[0])
            for flag_index in (6, 7, 8, 9, 10):
                self.assert_matches(row[flag_index], r'^(Yes|No)$', 'flag column')

    def test_access_points_structure(self):
        headers, rows, _ = threeBarsAccessPoints.__wrapped__(_Context(self.path))
        self.assert_row_shape(headers, rows)
        if not rows:
            self.skipTest('ZACCESSPOINT is empty in this image')
        self._assert_coordinates(rows, 1, 2)
        for row in rows:
            self.assert_plausible_timestamp(row[0])
            if row[3]:
                self.assert_matches(row[3], r'^([0-9a-f]{2}:){5}[0-9a-f]{2}$', 'BSSID')

    def test_tiles_structure(self):
        headers, rows, _ = threeBarsTiles.__wrapped__(_Context(self.path))
        self.assert_row_shape(headers, rows)
        if not rows:
            self.skipTest('ZTILE is empty in this image')
        for row in rows:
            self.assert_plausible_timestamp(row[0])


@unittest.skipUnless(LOCAL_IMAGE, 'set ILEAPP_LOCAL_IMAGE to run local corpus tests')
class LocationdCacheLocalTest(LocalCorpusTestCase):
    SUFFIX = 'Library/Caches/locationd/cache_encryptedB.db'

    def setUp(self):
        super().setUp()
        self.path = self.fetch(self.SUFFIX)
        if not self.path:
            self.skipTest(f'{self.SUFFIX} not present in {LOCAL_IMAGE}')
        self.fetch(self.SUFFIX + '-wal')
        self.fetch(self.SUFFIX + '-shm')

    def _assert_coordinates(self, rows, latitude_index=1, longitude_index=2):
        for row in rows:
            latitude, longitude = row[latitude_index], row[longitude_index]
            if latitude in (None, '') and longitude in (None, ''):
                continue
            self.assertTrue(-90 <= latitude <= 90,
                            f'latitude out of range; shape was {_redact(latitude)}')
            self.assertTrue(-180 <= longitude <= 180,
                            f'longitude out of range; shape was {_redact(longitude)}')

    def test_wifi_locations_structure(self):
        headers, rows, _ = locationdWifiLocations.__wrapped__(_Context(self.path))
        self.assert_row_shape(headers, rows)
        if not rows:
            self.skipTest('WifiLocation is empty in this image')
        self._assert_coordinates(rows, 2, 3)
        for row in rows:
            self.assert_plausible_timestamp(row[0])
            self.assert_plausible_timestamp(row[1])   # ALS query, iOS 26 and later
            self.assert_matches(row[4], r'^([0-9a-f]{2}:){5}[0-9a-f]{2}$', 'BSSID')

    def test_wifi_harvest_structure(self):
        headers, rows, _ = locationdWifiHarvest.__wrapped__(_Context(self.path))
        self.assert_row_shape(headers, rows)
        if not rows:
            self.skipTest('WifiAssociatedApWifiHarvestTable is empty in this image')
        self._assert_coordinates(rows, 2, 3)
        for row in rows:
            self.assert_plausible_timestamp(row[0])
            self.assert_plausible_timestamp(row[1])
            self.assert_matches(row[4], r'^([0-9a-f]{2}:){5}[0-9a-f]{2}$', 'BSSID')

    def test_cell_locations_structure(self):
        headers, rows, _ = locationdCellLocations.__wrapped__(_Context(self.path))
        self.assert_row_shape(headers, rows)
        if not rows:
            self.skipTest('no cell table holds rows in this image')
        self._assert_coordinates(rows)
        known_radios = {'GSM/UMTS', 'GSM/UMTS (Local)', 'LTE', 'LTE (Local)', '5G NR',
                        'TD-SCDMA', 'CDMA', 'CDMA (Local)'}
        for row in rows:
            self.assert_plausible_timestamp(row[0])
            self.assertIn(row[3], known_radios)

    def test_wifi_tiles_structure(self):
        headers, rows, _ = locationdWifiTiles.__wrapped__(_Context(self.path))
        self.assert_row_shape(headers, rows)
        if not rows:
            self.skipTest('WifiTileHeader is empty in this image')
        self._assert_coordinates(rows, 2, 3)
        for row in rows:
            self.assert_plausible_timestamp(row[0])
            self.assert_plausible_timestamp(row[1])


@unittest.skipUnless(LOCAL_IMAGE, 'set ILEAPP_LOCAL_IMAGE to run local corpus tests')
class PowerlogLocalTest(LocalCorpusTestCase):
    SUFFIX = 'Library/BatteryLife/CurrentPowerlog.PLSQL'

    def setUp(self):
        super().setUp()
        self.path = self.fetch(self.SUFFIX)
        if not self.path:
            self.skipTest(f'{self.SUFFIX} not present in {LOCAL_IMAGE}')

    def run_artifact(self, func):
        headers, rows, _ = func.__wrapped__(_Context(self.path))
        self.assert_row_shape(headers, rows)
        for row in rows:
            # Corrected timestamp first, applied offset second-to-last.
            self.assert_plausible_timestamp(row[0])
            if row[-2] is not None:
                self.assertIsInstance(row[-2], int)
        return rows

    def test_application_runtime_structure(self):
        for row in self.run_artifact(powerlogApplicationRuntime):
            if row[2] is not None:
                self.assertGreaterEqual(row[2], 0)   # Background Time
            if row[3] is not None:
                self.assertGreaterEqual(row[3], 0)   # Screen-on Time

    def test_battery_level_structure(self):
        for row in self.run_artifact(powerlogBatteryLevel):
            if row[1] is not None:
                self.assertTrue(0 <= row[1] <= 100,
                                f'battery level shape {_redact(row[1])}')
            self.assert_matches(row[2], r'^(Yes|No|\d+)$', 'Is Charging')

    def test_device_power_state_structure(self):
        self.run_artifact(powerlogDevicePowerState)

    def test_app_state_structure(self):
        for row in self.run_artifact(powerlogAppState):
            if row[3] is not None:
                self.assertIsInstance(row[3], int)   # State code as stored

    def test_device_lock_structure(self):
        for row in self.run_artifact(powerlogDeviceLock):
            self.assert_matches(row[1], r'^(Yes|No|\d+)$', 'Locked')

    def test_display_state_structure(self):
        for row in self.run_artifact(powerlogDisplayState):
            if row[1] is not None:
                self.assertTrue(0 <= row[1] <= 100,
                                f'brightness shape {_redact(row[1])}')

    def test_audio_routing_structure(self):
        for row in self.run_artifact(powerlogAudioRouting):
            self.assert_matches(row[1], r'^(Yes|No|\d+)$', 'Active')


@unittest.skipUnless(LOCAL_IMAGE, 'set ILEAPP_LOCAL_IMAGE to run local corpus tests')
class PowerTelemetryLocalTest(LocalCorpusTestCase):
    SUFFIX = 'Library/PerfPowerTelemetry/ExtendedPersistence/CurrentLog.EPSQL'

    def setUp(self):
        super().setUp()
        self.path = self.fetch(self.SUFFIX)
        if not self.path:
            self.skipTest(f'{self.SUFFIX} not present in {LOCAL_IMAGE}')

    def run_artifact(self, func):
        headers, rows, _ = func.__wrapped__(_Context(self.path))
        self.assert_row_shape(headers, rows)
        for row in rows:
            self.assert_plausible_timestamp(row[0])
            if row[-2] is not None:
                self.assertIsInstance(row[-2], int)   # applied offset
        return rows

    def test_battery_data_daily_structure(self):
        for row in self.run_artifact(powerTelemetryBatteryDataDaily):
            if row[1] is not None:
                self.assertGreaterEqual(row[1], 0)    # Cycle Count
            if row[2] is not None:
                self.assertTrue(0 <= row[2] <= 120,
                                f'max capacity shape {_redact(row[2])}')

    def test_smart_charging_structure(self):
        self.run_artifact(powerTelemetrySmartCharging)


@unittest.skipUnless(LOCAL_IMAGE, 'set ILEAPP_LOCAL_IMAGE to run local corpus tests')
class TelegramLocalTest(LocalCorpusTestCase):
    """Structural checks for the Telegram accounts/contacts/settings artifacts.

    These artifacts route files by their path tails (account-<id>/postbox vs
    accounts-metadata), so fetched files keep their trailing directories
    instead of being flattened into the temp directory.
    """

    # Tail patterns to mirror out of the image, with -wal/-shm companions so
    # recent rows are not lost for databases mid-checkpoint.
    TAILS = (
        re.compile(r'telegram-data/account-\d+/postbox/db/db_sqlite(-wal|-shm)?$'),
        re.compile(r'telegram-data/accounts-metadata/db/db_sqlite(-wal|-shm)?$'),
        re.compile(r'telegram-data/accounts-metadata/atomic-state$'),
    )
    TAIL_ANCHOR = 'telegram-data/'

    def setUp(self):
        super().setUp()
        self.paths = self.fetch_tree()
        if not any(p.replace(os.sep, '/').endswith('/postbox/db/db_sqlite')
                   for p in self.paths):
            self.skipTest(f'no Telegram postbox database in {LOCAL_IMAGE}')

    def fetch_tree(self):
        """Copy matching files out of the image, keeping the telegram-data tail."""
        found = []
        source = Path(LOCAL_IMAGE)

        def keep(name):
            normalized = name.replace(os.sep, '/')
            return any(tail.search(normalized) for tail in self.TAILS)

        def destination_for(name):
            normalized = name.replace(os.sep, '/')
            tail = normalized[normalized.rindex(self.TAIL_ANCHOR):]
            destination = Path(self.temp_dir.name) / tail
            destination.parent.mkdir(parents=True, exist_ok=True)
            return destination

        if source.is_dir():
            for candidate in source.rglob('*'):
                name = str(candidate)
                if candidate.is_file() and self.TAIL_ANCHOR in name.replace(os.sep, '/') \
                        and keep(name):
                    destination = destination_for(name)
                    shutil.copy2(candidate, destination)
                    found.append(str(destination))
        else:
            with zipfile.ZipFile(source) as archive:
                for name in archive.namelist():
                    if self.TAIL_ANCHOR in name and keep(name):
                        destination = destination_for(name)
                        with archive.open(name) as member, \
                                open(destination, 'wb') as out:
                            shutil.copyfileobj(member, out)
                        found.append(str(destination))
        return found

    def test_accounts_structure(self):
        from scripts.artifacts.telegramAccounts import telegramAccounts
        headers, rows, _ = telegramAccounts.__wrapped__(_ListContext(self.paths))
        self.assertTrue(rows, 'telegramAccounts parsed no rows')
        self.assert_row_shape(headers, rows)
        for row in rows:
            self.assert_plausible_timestamp(row[0])
            self.assert_matches(row[1], r'^\d+$', 'Account ID')
            self.assert_matches(row[2], r'^(Yes|)$', 'Active Account')
            if row[3]:
                self.assert_matches(row[3], r'^\d+$', 'User ID')
            if row[4]:
                self.assert_matches(row[4], r'^(Production|Test)$', 'Environment')

    def test_contacts_structure(self):
        from scripts.artifacts.telegramAccounts import telegramContacts
        headers, rows, _ = telegramContacts.__wrapped__(_ListContext(self.paths))
        self.assertTrue(rows, 'telegramContacts parsed no rows')
        self.assert_row_shape(headers, rows)
        for row in rows:
            self.assert_matches(row[0], r'^\d+$', 'Account ID')
            self.assert_matches(row[1], r'^-?\d+$', 'Peer ID')
            self.assert_matches(
                row[2], r'^(User|Group|Channel|Secret Chat|Unknown)$', 'Type')
            self.assertIsInstance(row[8], int)      # Messages In Chat
            self.assertGreaterEqual(row[8], 0)
            self.assert_matches(row[9], r'^(Yes|)$', 'In Contact List')
            self.assert_matches(row[10], r'^(Yes|)$', 'In Spotlight Cache')

    def test_chats_structure(self):
        from scripts.artifacts.telegramAccounts import telegramChats
        headers, rows, _ = telegramChats.__wrapped__(_ListContext(self.paths))
        self.assertTrue(rows, 'telegramChats parsed no rows')
        self.assert_row_shape(headers, rows)
        for row in rows:
            self.assert_plausible_timestamp(row[0])
            self.assert_matches(row[1], r'^\d+$', 'Account ID')
            self.assert_matches(row[2], r'^-?\d+$', 'Chat ID')
            self.assert_matches(row[5], r'^(Main|Archived)$', 'Folder')
            self.assert_matches(row[6], r'^(Yes|)$', 'Pinned')
            self.assertIsInstance(row[7], int)      # Messages Stored
            self.assertIsInstance(row[8], int)      # Unread Count
            self.assertGreaterEqual(row[8], 0)
            self.assert_matches(row[9], r'^(Yes|)$', 'Marked Unread')

    def test_cached_peer_data_structure(self):
        from scripts.artifacts.telegramAccounts import telegramCachedPeerData
        headers, rows, _ = telegramCachedPeerData.__wrapped__(_ListContext(self.paths))
        self.assertTrue(rows, 'telegramCachedPeerData parsed no rows')
        self.assert_row_shape(headers, rows)
        for row in rows:
            self.assert_matches(row[0], r'^\d+$', 'Account ID')
            self.assert_matches(row[1], r'^-?\d+$', 'Peer ID')
            self.assert_matches(
                row[3], r'^(User|Group|Channel|Secret Chat|Unknown)$', 'Record Type')
            if row[5]:                                  # Birthday, year optional
                self.assert_matches(row[5], r'^(\d{4}|--)-\d{2}-\d{2}$', 'Birthday')
            self.assert_matches(row[6], r'^(Yes|No|)$', 'Blocked')
            if row[7] != '':                            # Common Group Count
                self.assertIsInstance(row[7], int)
                self.assertGreaterEqual(row[7], 0)
            self.assert_matches(row[8], r'^(Yes|No|)$', 'Has Scheduled Messages')
            self.assert_matches(
                row[9], r'^(None set|\d+ seconds|)$', 'Auto-Delete Timer')
        # Blocked and common-group counts are user-only fields; channel records
        # encode 'b' as botInfos and must not be reported as a blocked state.
        for row in rows:
            if row[3] == 'Channel':
                self.assertEqual(row[6], '', 'channel record reported a Blocked value')

    def test_settings_structure(self):
        from scripts.artifacts.telegramAccounts import telegramSettings
        headers, rows, _ = telegramSettings.__wrapped__(_ListContext(self.paths))
        self.assertTrue(rows, 'telegramSettings parsed no rows')
        self.assert_row_shape(headers, rows)
        settings_seen = set()
        for row in rows:
            self.assert_matches(row[0], r'^(Shared|Account \d+)$', 'Scope')
            self.assertIsInstance(row[3], int)      # Key ID
            self.assertTrue(row[2], 'empty settings value')
            settings_seen.add(row[3])
        # The headline settings are reported even when the user never changed
        # them, so their key IDs are always present for each store that exists.
        self.assertIn(1020, settings_seen)          # save to Photos (per account)
        if any(p.replace(os.sep, '/').endswith('/accounts-metadata/db/db_sqlite')
               for p in self.paths):
            self.assertIn(1002, settings_seen)      # media auto-download (shared)


class _ListContext(_Context):
    """A context over several found files, as multi-path artifacts receive."""

    def __init__(self, paths):     # pylint: disable=super-init-not-called
        self.paths = [str(p) for p in paths]

    def get_files_found(self):
        return self.paths


if __name__ == '__main__':
    unittest.main()
