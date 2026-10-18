"""containerManagerState: iOS 27 logs/ContainerManager/state.json, SYNTHETIC input only."""
import importlib.util
import io
import json
import tarfile
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from scripts.artifacts import containerManagerState as module

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('synthetic_container_state', HERE / 'synthetic_container_state.py')
SYNTH = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SYNTH)


def _context(files):
    return SimpleNamespace(get_files_found=lambda: [str(path) for path in files],
                           get_relative_path=lambda value: Path(value.split(' >> ')[0]).name)


def _run(function, files):
    return function.__wrapped__(_context(files))


class ContainerManagerStateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = SYNTH.to_bytes(SYNTH.build_state())
        cls.expected = module.expected_counts(json.loads(cls.raw))

    def _standalone(self, folder, content):
        path = Path(folder) / 'ContainerManager' / 'state.json'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return path

    def test_row_counts_match_the_file(self):
        with tempfile.TemporaryDirectory() as folder:
            path = self._standalone(folder, self.raw)
            with_dir = _run(module.containerManagerState, [path])
            no_dir = _run(module.containerManagerStateNoDirectory, [path])
            signing = _run(module.containerManagerStateRegistrations, [path])
        self.assertEqual(len(with_dir[1]) + len(no_dir[1]), self.expected['container'])
        self.assertEqual(len(signing[1]), self.expected['codesign'])
        for headers, rows, _source in (with_dir, no_dir, signing):
            self.assertTrue(rows)
            self.assertTrue(all(len(row) == len(headers) for row in rows))

    def test_timeline_artifact_has_only_dated_rows_and_a_datetime_first_column(self):
        with tempfile.TemporaryDirectory() as folder:
            headers, rows, _ = _run(module.containerManagerState, [self._standalone(folder, self.raw)])
        self.assertEqual(headers[0][1], 'datetime')
        self.assertTrue(all(row[0] is not None and row[0].tzinfo is not None for row in rows))
        row = next(row for row in rows if row[1] == 'Data/Application')
        self.assertTrue(row[5].endswith(row[6]))        # the path ends in the directory name
        self.assertNotEqual(row[6], row[7])             # the directory name is not the container uuid

    def test_no_directory_rows_carry_no_time(self):
        with tempfile.TemporaryDirectory() as folder:
            headers, rows, _ = _run(module.containerManagerStateNoDirectory, [self._standalone(folder, self.raw)])
        self.assertFalse(any(isinstance(header, tuple) for header in headers))
        self.assertTrue(all(row[5] == -1 for row in rows))

    def test_sysdiagnose_archive_reads_only_the_container_manager_file(self):
        with tempfile.TemporaryDirectory() as folder:
            archive = Path(folder) / 'sysdiagnose_2026.09.29_19-00-00-0400_iPhone-OS_iPhone_00A000.tar.gz'
            with tarfile.open(archive, 'w:gz') as tar:
                for name, payload in (('sysdiagnose_x/logs/ContainerManager/state.json', self.raw),
                                      ('sysdiagnose_x/other/state.json', b'{"a": 1}')):
                    info = tarfile.TarInfo(name)
                    info.size = len(payload)
                    tar.addfile(info, io.BytesIO(payload))
            headers, rows, source = _run(module.containerManagerState, [archive])
            missing = len(_run(module.containerManagerStateNoDirectory, [archive])[1])
        self.assertEqual(len(rows) + missing, self.expected['container'])
        self.assertIn(' >> sysdiagnose_x/logs/ContainerManager/state.json', source)
        self.assertEqual(len(headers), len(rows[0]))

    def test_damaged_and_unrelated_files_give_no_rows_and_no_crash(self):
        cases = dict(SYNTH.edge_cases())
        for name in ('empty_file', 'truncated_json', 'not_json', 'root_is_list', 'empty_object', 'wrong_types',
                     'bad_timestamps', 'huge_numbers', 'missing_fields', 'unknown_keys', 'flags'):
            with self.subTest(case=name), tempfile.TemporaryDirectory() as folder, \
                    patch.object(module, 'logfunc'):
                path = self._standalone(folder, cases[name])
                for function in (module.containerManagerState, module.containerManagerStateNoDirectory,
                                 module.containerManagerStateRegistrations):
                    headers, rows, _ = _run(function, [path])
                    self.assertTrue(all(len(row) == len(headers) for row in rows))
        with tempfile.TemporaryDirectory() as folder:
            stray = Path(folder) / 'state.json'
            stray.write_bytes(self.raw)
            self.assertEqual(_run(module.containerManagerState, [stray])[1], [])

    def test_bad_times_are_blank_not_invented(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(module, 'logfunc'):
            path = self._standalone(folder, SYNTH.edge_cases()['bad_timestamps'])
            _, rows, _ = _run(module.containerManagerState, [path])
        self.assertTrue(all(row[0] is None or row[0].year < 2100 for row in rows))
        self.assertIsNone(rows[0][0])


if __name__ == '__main__':
    unittest.main()
