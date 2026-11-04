"""The DMSS database artifacts read a store in WAL mode instead of stopping on its sidecars.

Devices.sqlite3* and DMSSCloud.sqlite* also match the -wal and -shm files beside a store in
WAL mode. Each artifact queried every match, and a sidecar raises sqlite3.DatabaseError
('file is not a database'), which none of them caught: Channels and Info caught nothing,
Sensors and Devices only OperationalError. So the artifact stopped and reported nothing.
These tests build both stores in WAL mode, with uncheckpointed rows in the -wal, and run
the artifacts over every file the patterns match.
"""
import os
import shutil
import sqlite3
import tempfile
import unittest

from scripts.artifacts import dmss
from scripts.context import Context

SUPPORT = 'private/var/mobile/Containers/Data/Application/A/Library/Support'


def wal_store(path, script):
    """Create a store in WAL mode whose rows are still only in the -wal; return the open
    writer, which keeps the sidecars in place until it is closed."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    writer = sqlite3.connect(path)
    writer.execute('PRAGMA journal_mode=WAL')
    writer.execute('PRAGMA wal_autocheckpoint=0')
    writer.executescript(script)
    writer.commit()
    return writer


class DmssWalSidecarsTest(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.data = os.path.join(self.tmpdir, 'data')
        support = os.path.join(self.data, SUPPORT)
        self.writers = [
            wal_store(os.path.join(support, 'Devices.sqlite3'), '''
                CREATE TABLE DEVICES(ID INTEGER, NAME TEXT, IP TEXT, PORT INT, USER TEXT, PASSWORD TEXT);
                CREATE TABLE CHANNELS(CHANNELID INT, NAME TEXT, DEVICEID INT);
                CREATE TABLE DDNSCONFIG(DEVICEID TEXT, DDNSENABLE TEXT, DDNSADDRESS TEXT, DDNSDOMAIN TEXT,
                    DDNSSERVERPORT INT, DDNSUSERNAME TEXT, DDNSPASSWORD TEXT, DDNSTYPE TEXT, DDNSALIAS TEXT);
                INSERT INTO DEVICES VALUES (1, 'Camera', '10.0.0.2', 37777, 'admin', 'x');
                INSERT INTO CHANNELS VALUES (0, 'Door', 1);
                INSERT INTO DDNSCONFIG VALUES ('10.0.0.2', '1', 'a', 'b', 80, 'u', 'p', 't', 'al');'''),
            wal_store(os.path.join(support, '0', 'DMSSCloud.sqlite'), '''
                CREATE TABLE GatewayPartTable(partName, partModel, partSN, paasType, alarmState,
                    batteryPercent, boxSN, onLineState, doorState, fullDayAlarm, tamper);
                CREATE TABLE DEVICES(name, serial, sn, devType, channelCount, deviceIsOnline, ReceiveShare,
                    SendShareStr, userName, DeviceCS, SupCaps, ChannelCS, mPort, mRtspPort, hwId);
                INSERT INTO GatewayPartTable VALUES ('Sensor', 'M', 'S1', 't', '1', 90, 'H', '1', 0, '0', 0);
                INSERT INTO DEVICES VALUES ('Hub', 's', 'SN', 'd', 1, 1, '', '', 'u', '', '', '', 1, 2, 'hw');'''),
        ]
        Context.clear()
        Context.set_data_folder(self.data)

    def tearDown(self):
        for writer in self.writers:
            writer.close()
        Context.clear()
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def matches(self, name):
        found = []
        for folder, _, files in os.walk(self.data):
            found += [os.path.join(folder, f) for f in files if f.startswith(name)]
        self.assertTrue(any(f.endswith('-wal') for f in found), found)
        return sorted(found)

    def run_artifact(self, function, name):
        Context.set_files_found(self.matches(name))
        _, rows, source = function.__wrapped__(Context)
        return rows, source

    def test_every_store_artifact_reads_the_wal_mode_store(self):
        for function, name in ((dmss.get_dmss_channels, 'Devices.sqlite3'),
                               (dmss.get_dmss_info, 'Devices.sqlite3'),
                               (dmss.get_dmss_registered_sensors, 'DMSSCloud.sqlite'),
                               (dmss.get_dmss_registered_devices, 'DMSSCloud.sqlite')):
            rows, _ = self.run_artifact(function, name)
            self.assertEqual(len(rows), 1, function.__name__)

    def test_rows_name_the_database_not_a_sidecar(self):
        rows, _ = self.run_artifact(dmss.get_dmss_channels, 'Devices.sqlite3')

        self.assertEqual(rows[0][:3], ('Camera', 0, 'Door'))
        self.assertEqual(rows[0][-1], f'{SUPPORT}/Devices.sqlite3')


if __name__ == '__main__':
    unittest.main()
