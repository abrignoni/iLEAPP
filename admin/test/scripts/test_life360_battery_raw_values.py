"""Exercise parsed device values and occurrence/source retention in actual log files."""
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from scripts.artifacts.life360 import life360DeviceBattery, life360Locations


class BatteryValuesTests(unittest.TestCase):
    def test_typed_values_and_repeated_lines(self):
        values = ['0', '1', '', 'unknown', 0, 1, False, True, 0.0, 1.0,
                  None, [0, False], {'x': '1'}]
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            path = root / 'com.life360.safetymap a.log'
            rows = [{'geolocation': {'timestamp': 1704164645, 'lat': 1, 'lon': 2},
                     'device': {'battery': 42, 'charge': value}} for value in values]
            rows.extend([{'geolocation': {'timestamp': 1704164645}, 'device': {}}, rows[0]])
            path.write_text('ignored\nX-UserContext header set: {bad}\n' + ''.join(
                'X-UserContext header set: ' + json.dumps(row) + '\n' for row in rows))
            context = SimpleNamespace(get_files_found=lambda: [str(path)],
                                      get_relative_path=lambda value: Path(value).name)
            _, result, source = life360DeviceBattery.__wrapped__(context)
            self.assertEqual(len(result), len(rows))
            expected = values + ['', '0']
            self.assertEqual([(type(row[2]), row[2]) for row in result],
                             [(type(value), value) for value in expected])
            self.assertEqual([row[1] for row in result], [42] * len(values) + ['', 42])
            self.assertEqual(source, path.name)
            self.assertEqual(len(life360Locations.__wrapped__(context)[1]), len(rows))

    def test_encounter_order_and_missing_timestamp(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            files = []
            for name, charge in [('b', '1'), ('a', '0')]:
                path = root / (name + '.log')
                path.write_text('X-UserContext header set: ' + json.dumps(
                    {'device': {'charge': charge}}) + '\n')
                files.append(str(path))
            empty = root / 'empty.log'
            empty.write_text('nothing\n')
            files.append(str(empty))
            context = SimpleNamespace(get_files_found=lambda: files,
                                      get_relative_path=lambda value: Path(value).name)
            _, rows, source = life360DeviceBattery.__wrapped__(context)
            self.assertEqual(rows, [('', '', '1'), ('', '', '0')])
            self.assertEqual(source, 'b.log\na.log\nempty.log')


if __name__ == '__main__':
    unittest.main()
