"""Synthetic iOS discovery and source-path tests; no real iOS acquisition."""
import fnmatch
import hashlib
import plistlib
import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from scripts.artifacts import djiFlightRecordTxt as module
from scripts.search_files import FileSeekerItunes
from admin.test.scripts.test_dji_txt_parser import log, record, osd


class IOSDiscoveryTests(unittest.TestCase):
    def test_document_paths_and_exclusions(self):
        pattern = module.__artifacts_v2__['djiFlightRecordTxtRecords']['paths'][0]
        for root in ('root/private/var/mobile/Containers/Data/Application/UUID',
                     'root/Applications/SYNTHETIC-APP',
                     'private/var/mobile/Containers/Data/Application/synthetic.dji'):
            self.assertTrue(fnmatch.fnmatchcase(root + '/Documents/FlightRecords/DJIFlightRecord_test.txt', pattern))
        for path in ('root/Android/data/dji.go.v5/files/FlightRecord/DJIFlightRecord_test.txt',
                     'root/Documents/FlightRecords/export.csv',
                     'root/Documents/Logs/DJIFlightRecord_test.txt'):
            self.assertFalse(fnmatch.fnmatchcase(path, pattern))

    def test_multiple_sources_relative_rows_and_no_evidence_writes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = root / 'Documents/FlightRecords/DJIFlightRecord_one.txt'
            first.parent.mkdir(parents=True)
            first.write_bytes(log(6, record(1, osd(), 6)))
            second = first.with_name('DJIFlightRecord_unsupported.txt')
            second.write_bytes(log(15))
            files = [str(first), str(first), str(second)]
            before = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in (first, second)}
            context = SimpleNamespace(get_files_found=lambda: files,
                                      get_relative_path=lambda p: Path(p).relative_to(root).as_posix())
            with patch.object(module, 'logfunc'):
                headers, rows, sources = module.djiFlightRecordTxtSummary.__wrapped__(context)
                self.assertEqual(sources.splitlines(), [str(first), str(second)])
                self.assertEqual(len(rows), 2)
                self.assertIn('Unsupported DJI TXT version 15', rows[1][2])
                self.assertEqual(rows[0][-1], first.relative_to(root).as_posix())
                self.assertEqual(headers[0], ('Timestamp', 'datetime'))
                _, records, record_sources = module.djiFlightRecordTxtRecords.__wrapped__(context)
                self.assertEqual(len(records), 1)
                self.assertEqual(record_sources, sources)
                self.assertIsNone(records[0][0])
            self.assertEqual(before, {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in (first, second)})

    def test_unencrypted_itunes_appdomain_discovery(self):
        # Invented bundle ID: this tests seeker reconstruction, not DJI identity.
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            backup, stage = root / 'backup', root / 'stage'
            backup.mkdir(); stage.mkdir()
            relative = 'Documents/FlightRecords/DJIFlightRecord_synthetic.txt'
            domain = 'AppDomain-synthetic.dji'
            file_id = hashlib.sha1(f'{domain}-{relative}'.encode()).hexdigest()
            stored = backup / file_id[:2] / file_id
            stored.parent.mkdir()
            contents = log(6, record(1, osd(), 6))
            stored.write_bytes(contents)
            with closing(sqlite3.connect(backup / 'Manifest.db')) as db:
                db.execute('CREATE TABLE Files(fileID TEXT, domain TEXT, relativePath TEXT, flags INTEGER, file BLOB)')
                db.execute('INSERT INTO Files VALUES (?,?,?,?,?)',
                           (file_id, domain, relative, 1, plistlib.dumps({'Birth': 0, 'LastModified': 0})))
                db.commit()
            (backup / 'Manifest.plist').write_bytes(plistlib.dumps({'IsEncrypted': False}))
            seeker = FileSeekerItunes(str(backup), str(stage), 'db', None)
            pattern = module.__artifacts_v2__['djiFlightRecordTxtRecords']['paths'][0]
            matches = list(seeker.search(pattern))
            self.assertEqual(len(matches), 1)
            self.assertEqual(Path(matches[0]).read_bytes(), contents)
            self.assertEqual(stored.read_bytes(), contents)


if __name__ == '__main__':
    unittest.main()
