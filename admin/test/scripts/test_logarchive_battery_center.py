"""Pin how the Battery Center artifacts split a unified log entry into columns.

Battery Center writes a power source as an NSDictionary description, one 'key = value;' line
per key between braces, and a device as '<BCBatteryDevice: 0x...; key = value; ...>'. The
messages below are synthetic and follow those two shapes. The expected rows are written out,
never read back from the code.

Both artifacts select from the table logarchive_artifacts builds, so the last class checks
that the broad query collects what the two narrow ones ask for.
"""
import datetime
import pathlib
import sqlite3
import sys
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts.artifacts import logarchive as module  # pylint: disable=wrong-import-position

SOURCE = '''(<_BCPowerSourceController: 0x100000000>) Found power source: {
    "Battery Provides Time Remaining" = 1;
    "Current Capacity" = 97;
    "Cycle count" = 123;
    "Is Charged" = 0;
    "Is Charging" = 1;
    "Is Finishing Charge" = 0;
    "Is Present" = 1;
    "LPM Active" = 0;
    "Max Capacity" = 100;
    Name = "Test\\U2019s \\"Battery\\"; one = two";
    "Play Charging Chime" = 1;
    "Power Source ID" = 1234;
    "Power Source State" = "AC Power";
    "Raw External Connected" = 1;
    "Show Charging UI" = 1;
    "Transport Type" = Internal;
    Type = InternalBattery;
    BatteryHealthCondition = "";
}'''

DEVICE = ('(<_BCPowerSourceController: 0x100000000>) Found device: <BCBatteryDevice: 0x200000000; '
          'vendor = Apple; productIdentifier = 0; parts = (null); identifier = 1234; '
          'matchIdentifier = (null); name = Test; Phone; groupName =InternalBattery-0; '
          'percentCharge = 77; lowBattery = NO; connected = YES; charging = NO; internal = YES; '
          'powerSource = YES; poweredSoureState = Battery Power; transportType = Internal; '
          'accessoryIdentifier = (null); accessoryCategory = Unknown; modelNumber = (null); >')


class BatteryCenterSourceTests(unittest.TestCase):

    def test_shown_keys_fill_their_columns_and_the_rest_go_to_other(self):
        pairs, leftover = module._bc_source_pairs(SOURCE)  # pylint: disable=protected-access
        row = module._bc_row(pairs, leftover, module._BC_SOURCE_KEYS)  # pylint: disable=protected-access
        self.assertEqual(row, (
            'Test’s "Battery"; one = two', 'InternalBattery', 'Internal', 'AC Power', '97', '100',
            '1', '0', '0', '1', '1', '1', '1', '123', '', '', '', '1234',
            'Battery Provides Time Remaining = 1; LPM Active = 0; BatteryHealthCondition = '))

    def test_a_key_without_a_column_is_kept(self):
        message = 'Found power source: {\n    Name = One;\n    "Product ID" = "00-11";\n}'
        pairs, leftover = module._bc_source_pairs(message)  # pylint: disable=protected-access
        row = module._bc_row(pairs, leftover, module._BC_SOURCE_KEYS)  # pylint: disable=protected-access
        self.assertEqual((row[0], row[-1]), ('One', 'Product ID = 00-11'))

    def test_a_nested_value_stays_one_value(self):
        message = ('Found power source: {\n    Name = One;\n    Details = {\n        Name = Inner;\n'
                   '        Parts = (\n            Left\n        );\n    };\n    Type = Two;\n}')
        pairs, leftover = module._bc_source_pairs(message)  # pylint: disable=protected-access
        row = module._bc_row(pairs, leftover, module._BC_SOURCE_KEYS)  # pylint: disable=protected-access
        self.assertEqual(row[:2], ('One', 'Two'))
        self.assertEqual(row[-1], 'Details = {Name = Inner; Parts = ( Left );}')

    def test_an_entry_cut_short_keeps_what_was_logged(self):
        for cut, other in (('    Type = Tw', 'Type = Tw'),
                           ('    Details = {\n        Inner = 1;', 'Details = {Inner = 1;'),
                           ('    Details = {\n        Inner = 1;\n    };', 'Details = {Inner = 1;}')):
            pairs, leftover = module._bc_source_pairs(  # pylint: disable=protected-access
                'Found power source: {\n    Name = One;\n' + cut)
            row = module._bc_row(pairs, leftover, module._BC_SOURCE_KEYS)  # pylint: disable=protected-access
            self.assertEqual((row[0], row[1], row[-1]), ('One', '', other))

    def test_a_line_that_is_not_a_pair_is_kept(self):
        message = 'Found power source: {\n    Name = One;\n    not a pair\n}'
        pairs, leftover = module._bc_source_pairs(message)  # pylint: disable=protected-access
        row = module._bc_row(pairs, leftover, module._BC_SOURCE_KEYS)  # pylint: disable=protected-access
        self.assertEqual((row[0], row[-1]), ('One', 'not a pair'))

    def test_a_message_without_braces_is_kept_whole(self):
        pairs, leftover = module._bc_source_pairs('Found power source: <private>')  # pylint: disable=protected-access
        row = module._bc_row(pairs, leftover, module._BC_SOURCE_KEYS)  # pylint: disable=protected-access
        self.assertEqual(row, ('',) * 18 + ('Found power source: <private>',))

    def test_a_repeated_key_keeps_the_first_in_its_column_and_the_next_in_other(self):
        message = 'Found power source: {\n    Name = One;\n    Name = Two;\n}'
        pairs, leftover = module._bc_source_pairs(message)  # pylint: disable=protected-access
        row = module._bc_row(pairs, leftover, module._BC_SOURCE_KEYS)  # pylint: disable=protected-access
        self.assertEqual((row[0], row[-1]), ('One', 'Name = Two'))


class BatteryCenterDeviceTests(unittest.TestCase):

    def test_device_values_fill_their_columns(self):
        pairs, leftover = module._bc_device_pairs(DEVICE)  # pylint: disable=protected-access
        row = module._bc_row(pairs, leftover, module._BC_DEVICE_KEYS)  # pylint: disable=protected-access
        self.assertEqual(row, (
            'Test; Phone', 'InternalBattery-0', 'Apple', '(null)', '77', 'NO', 'YES', 'YES',
            'Battery Power', 'Internal', '(null)', 'Unknown', '1234', '0',
            'parts = (null); matchIdentifier = (null); lowBattery = NO; powerSource = YES'))

    def test_a_message_of_another_shape_is_kept_whole(self):
        pairs, leftover = module._bc_device_pairs('Found device: <private>')  # pylint: disable=protected-access
        row = module._bc_row(pairs, leftover, module._BC_DEVICE_KEYS)  # pylint: disable=protected-access
        self.assertEqual(row, ('',) * 14 + ('Found device: <private>',))


class BatteryCenterSelectionTests(unittest.TestCase):
    """Run the three queries over a fixture shaped like the imported table."""

    ROWS = (
        (1704281051.485265, 1, '/SpringBoard', 33, 'com.apple.BatteryCenter', 'PowerSourceController', SOURCE, ''),
        (1704281051.5, 2, '/SpringBoard', 33, 'com.apple.BatteryCenter', 'PowerSourceController', DEVICE, ''),
        (1704281052.0, 3, '/SpringBoard', 33, 'com.apple.BatteryCenter', 'PowerSourceController',
         '(<_BCPowerSourceController: 0x100000000>) Found 1 power sources', ''),
        (1704281053.0, 4, '/other', 44, 'com.example.other', 'x', SOURCE, ''),
    )

    def setUp(self):
        self.db = sqlite3.connect(':memory:')
        self.addCleanup(self.db.close)
        self.db.execute('''CREATE TABLE logarchive (timestamp INTEGER, row_number TEXT,
            process_image_path TEXT, process_id TEXT, subsystem TEXT, category TEXT,
            event_message TEXT, trace_id TEXT)''')
        self.db.executemany('INSERT INTO logarchive VALUES (?,?,?,?,?,?,?,?)', self.ROWS)

    @staticmethod
    def _where(function_name, quote):
        source = pathlib.Path(module.__file__).read_text(encoding='utf-8')
        query = source.split(f'def {function_name}', 1)[1].split(quote)[1]
        return query.split('WHERE', 1)[1] if 'WHERE' in query else query

    def _selected(self, table, where):
        return [row[0] for row in self.db.execute(
            f'SELECT row_number FROM {table} WHERE {where} ORDER BY rowid')]

    def test_the_broad_query_collects_what_the_two_artifacts_select(self):
        broad = self._where('logarchive_artifacts', "'''")
        self.assertEqual(self._selected('logarchive', broad), ['1', '2'])
        self.db.execute(f'CREATE TABLE logarchive_artifacts AS SELECT * FROM logarchive WHERE {broad}')
        sources = self._where('logarchive_battery_center_sources', '"""')
        devices = self._where('logarchive_battery_center_devices', '"""')
        self.assertEqual(self._selected('logarchive_artifacts', sources), ['1'])
        self.assertEqual(self._selected('logarchive_artifacts', devices), ['2'])

    def test_the_table_time_becomes_a_utc_datetime(self):
        self.assertEqual(
            module._bc_time(1704281051.485265),  # pylint: disable=protected-access
            datetime.datetime(2024, 1, 3, 11, 24, 11, 485265, tzinfo=datetime.timezone.utc))
        self.assertEqual(module._bc_time(''), '')  # pylint: disable=protected-access


if __name__ == '__main__':
    unittest.main()
