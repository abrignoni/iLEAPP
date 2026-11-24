"""A DKEvent record that lacks a required field is skipped and logged, and the other rows stay.

SYNTHETIC records: the SEGB reader and the protobuf decoder are replaced, so each module sees one good
record and one with a field removed or of the wrong type.
"""
import fnmatch
import importlib
import os
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock

from admin.test.scripts.test_biome_dkevent_bad_dates import GOOD, payload, record

# The top-level fields whose absence skips the record.
MODULES = {
    'biomeAirpMode': ('get_biomeAirpMode', ('1', '2', '3', '5')),
    'biomeBattperc': ('get_biomeBattperc', ('1', '2', '3', '4', '5', '8')),
    'biomeCarplayisconnected': ('get_biomeCarplayisconnected', ('1', '2', '3', '4', '5', '8')),
    'biomeDevplugin': ('get_biomeDevplugin', ('1', '2', '3', '4', '5', '8')),
    'biomeSafari': ('get_biomeSafari', ('1', '2', '4', '5', '6')),
    'biomeWifi': ('get_biomeWifi', ('1', '2', '4', '5')),
}


class MissingFieldTest(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = temp.name

    def run_module(self, name, bad):
        module = importlib.import_module(f'scripts.artifacts.{name}')
        spec = next(iter(module.__artifacts_v2__.values()))
        pattern = spec['paths'][0] if isinstance(spec['paths'], tuple) else spec['paths']
        folder = os.path.join(self.root, pattern.strip('*/').rstrip('/*').replace('[Bb]', 'B'))
        os.makedirs(folder, exist_ok=True)
        segb = os.path.join(folder, '700000000000000')
        open(segb, 'wb').close()
        self.assertTrue(fnmatch.fnmatch(segb, pattern), 'the synthetic file sits where the module looks')
        context = SimpleNamespace(get_files_found=lambda: [segb], get_relative_path=os.path.basename)
        decoded = {b'good': payload(GOOD), b'bad': bad}
        records = [record(8, b'good'), record(64, b'bad')]
        with mock.patch.object(module, 'read_segb_file', return_value=records), \
                mock.patch.object(module.blackboxprotobuf, 'decode_message',
                                  side_effect=lambda data, _types: (decoded[data], {})), \
                mock.patch.object(module, 'logfunc') as log:
            _, rows, _ = getattr(module, MODULES[name][0]).__wrapped__(context)
        return rows, ' '.join(str(call.args[0]) for call in log.call_args_list), os.path.basename(segb)

    def check_skipped(self, name, bad):
        rows, logged, segb_name = self.run_module(name, bad)
        self.assertEqual(len(rows), 1, 'the good record is reported and the bad one is not')
        self.assertIn('offset 64', logged)
        self.assertIn(segb_name, logged)
        self.assertIn('could not be read', logged)

    def test_a_missing_field_skips_only_that_record(self):
        for name, (_, fields) in MODULES.items():
            for field in fields:
                with self.subTest(module=name, field=field):
                    bad = payload(GOOD)
                    del bad[field]
                    self.check_skipped(name, bad)

    def test_a_field_of_the_wrong_shape_skips_only_that_record(self):
        # Only fields the module indexes into or decodes; a field it reports as stored keeps its row.
        indexed = {'biomeAirpMode': '15', 'biomeBattperc': '14', 'biomeCarplayisconnected': '14',
                   'biomeDevplugin': '14', 'biomeSafari': '146', 'biomeWifi': '145'}
        for name, fields in indexed.items():
            for field in fields:
                with self.subTest(module=name, field=field):
                    bad = payload(GOOD)
                    bad[field] = 7
                    self.check_skipped(name, bad)


if __name__ == '__main__':
    unittest.main()
