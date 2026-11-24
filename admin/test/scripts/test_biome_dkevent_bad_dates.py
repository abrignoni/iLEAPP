"""A DKEvent record with a date no datetime can hold keeps its row with an empty date (issue 2863).

SYNTHETIC records: the SEGB reader and the protobuf decoder are replaced, so each module sees one good
record and one whose Start Date is not a usable number.
"""
import datetime
import fnmatch
import importlib
import os
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock

from scripts.ccl_segb.ccl_segb_common import EntryState

GOOD = 800_000_000.0
MODULES = {
    'biomeAirpMode': 'get_biomeAirpMode',
    'biomeAppinstall': 'get_biomeAppinstall',
    'biomeBattperc': 'get_biomeBattperc',
    'biomeCarplayisconnected': 'get_biomeCarplayisconnected',
    'biomeDKInfocus': 'get_biomeDKInfocus',
    'biomeDKKeybag': 'get_biomeDKKeybag',
    'biomeDevplugin': 'get_biomeDevplugin',
    'biomeLocationactivity': 'get_biomeLocationactivity',
    'biomeSafari': 'get_biomeSafari',
    'biomeWifi': 'get_biomeWifi',
}


def payload(start):
    return {
        '1': {'1': '/stream', '2': {'1': 1, '2': 1}},
        '2': start,
        '3': GOOD + 60,
        '4': {'1': {'1': 1, '2': 1}, '3': b'com.example.app', '4': 1, '5': 50.0},
        '5': b'00000000-0000-0000-0000-000000000000',
        '6': {'1': b'source', '2': b'com.example.source', '4': b'detail'},
        '7': [],
        '8': GOOD + 120,
        '10': 0,
    }


def record(offset, data):
    return SimpleNamespace(timestamp1=datetime.datetime(2026, 1, 1), state=EntryState.Written, data=data,
                           data_start_offset=offset)


class BadDateTest(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = temp.name

    def run_module(self, name, bad_start, field='2'):
        module = importlib.import_module(f'scripts.artifacts.{name}')
        spec = next(iter(module.__artifacts_v2__.values()))
        pattern = spec['paths'][0] if isinstance(spec['paths'], tuple) else spec['paths']
        folder = os.path.join(self.root, pattern.strip('*/').rstrip('/*').replace('[Bb]', 'B'))
        os.makedirs(folder, exist_ok=True)
        segb = os.path.join(folder, '700000000000000')
        open(segb, 'wb').close()
        self.assertTrue(fnmatch.fnmatch(segb, pattern), 'the synthetic file sits where the module looks')
        context = SimpleNamespace(get_files_found=lambda: [segb], get_relative_path=os.path.basename)
        bad = payload(GOOD)
        bad[field] = bad_start
        decoded = {b'good': payload(GOOD), b'bad': bad}
        records = [record(8, b'good'), record(64, b'bad')]
        with mock.patch.object(module, 'read_segb_file', return_value=records), \
                mock.patch.object(module.blackboxprotobuf, 'decode_message',
                                  side_effect=lambda data, _types: (decoded[data], {})), \
                mock.patch('scripts.biome_stream_records.logfunc') as log:
            _, rows, _ = getattr(module, MODULES[name]).__wrapped__(context)
        return rows, ' '.join(str(call.args[0]) for call in log.call_args_list), os.path.basename(segb)

    def test_bad_start_date_keeps_the_row(self):
        for name in MODULES:
            for bad in (float('nan'), float('inf'), 1e300):
                with self.subTest(module=name, value=bad):
                    rows, logged, segb_name = self.run_module(name, bad)
                    self.assertEqual(len(rows), 2, 'both records are reported')
                    self.assertIn(rows[1][1], (None, ''), 'the bad Start Date is empty')
                    self.assertIsInstance(rows[0][1], datetime.datetime, 'the good Start Date converts')
                    self.assertIn('offset 64', logged)
                    self.assertIn(segb_name, logged)

    def test_bad_end_and_creation_dates_keep_the_row(self):
        fields = {'biomeAirpMode': '3', 'biomeAppinstall': '38', 'biomeBattperc': '38',
                  'biomeCarplayisconnected': '38', 'biomeDKInfocus': '38', 'biomeDKKeybag': '3',
                  'biomeDevplugin': '38', 'biomeLocationactivity': '38', 'biomeWifi': '3'}
        for name, wanted in fields.items():
            for field in wanted:
                with self.subTest(module=name, field=field):
                    rows, logged, _ = self.run_module(name, float('nan'), field)
                    self.assertEqual(len(rows), 2, 'both records are reported')
                    self.assertIn('offset 64', logged)
                    self.assertEqual(sum(value is None for value in rows[1]) - sum(value is None for value in rows[0]),
                                     1, 'exactly one more empty value on the bad record')

    def test_repeated_date_field_keeps_the_row_and_its_other_fields(self):
        # blackboxprotobuf returns a list when a field repeats, which the conversion rejects with TypeError
        for name in MODULES:
            with self.subTest(module=name):
                rows, logged, _ = self.run_module(name, [GOOD, GOOD + 1])
                self.assertEqual(len(rows), 2, 'both records are reported')
                self.assertIn(rows[1][1], (None, ''), 'the repeated Start Date is empty')
                self.assertIn('TypeError', logged)
                self.assertIn('offset 64', logged)
                kept = [value for value in rows[1] if value not in (None, '')]
                expected = [value for value in rows[0] if value not in (None, '')]
                self.assertEqual(len(kept), len(expected) - 1, 'only the Start Date is lost')


if __name__ == '__main__':
    unittest.main()
