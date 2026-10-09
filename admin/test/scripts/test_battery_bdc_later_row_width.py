"""A short later BDC row must not discard either supported neighboring row."""
import csv
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from scripts.artifacts import batteryBDC


class BatteryBDCLaterRowWidthTest(unittest.TestCase):
    def test_supported_short_supported_preserves_typed_rows(self):
        first = ['raw-first', 'unused', '4200', '1', '2500', '-100', 'unused',
                 '4000', '80'] + ['unused'] * 9 + ['4.2']
        last = ['raw-last', 'unused', '4100', '2', '3000', '-200', 'unused',
                '4100', '79']
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'BDC_SBC_control.csv'
            with path.open('w', encoding='utf-8', newline='') as stream:
                csv.writer(stream).writerows([['header'] * 19, first, ['short'] * 8, last])
            context = SimpleNamespace(get_files_found=lambda: [str(path)],
                                      get_relative_path=lambda value: Path(value).name)
            with patch.object(batteryBDC, 'logfunc') as log:
                headers, rows, source = batteryBDC.battery_bdc.__wrapped__(context)
            expected = [
                ('raw-first', '80', '4200', 'Yes', 77.0, 25.0, '-100', '4000',
                 '4.2', path.name),
                ('raw-last', '79', '4100', 2, 86.0, 30.0, '-200', '4100',
                 '', path.name),
            ]
            self.assertEqual(len(headers), 10)
            self.assertEqual(rows, expected)
            self.assertEqual([[type(cell) for cell in row] for row in rows],
                             [[type(cell) for cell in row] for row in expected])
            self.assertEqual(source, folder)
            log.assert_called_once_with(
                'Skipping BDC data row: expected at least 9 columns, found 8')


if __name__ == '__main__':
    unittest.main()
