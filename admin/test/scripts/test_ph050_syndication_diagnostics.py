"""Unsupported and missing-main paths must not query a Syndication store."""
import sqlite3
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from scripts.artifacts import Ph050AssetIntResouData as parser


class TestSyndicationDiagnostics(unittest.TestCase):
    def test_unsupported_guard_and_fallback_do_not_read_database(self):
        with tempfile.TemporaryDirectory() as directory:
            main = Path(directory) / 'Photos.sqlite'
            with sqlite3.connect(main) as db:
                db.execute('CREATE TABLE unrelated(value)')
            sidecar = str(main) + '-wal'
            for version in ['12.4', '13.7', '13.8', '27.0']:
                with self.subTest(version=version):
                    context = SimpleNamespace(
                        get_files_found=lambda: [sidecar, str(main)],
                        get_report_folder=lambda: directory)
                    with patch.object(parser.iOS, 'get_version', return_value=version), \
                            patch.object(parser, 'logfunc') as logger, \
                            patch.object(parser, 'null_absent_columns') as compiler, \
                            patch.object(parser, 'get_sqlite_db_records') as reader:
                        result = parser.Ph050_2AssetIntResouSyndPL.__wrapped__(context)
                    self.assertEqual(result, ((), [], str(main)))
                    reader.assert_not_called()
                    compiler.assert_not_called()
                    logger.assert_called_once_with(
                        'Unsupported version for Syndication.photoslibrary from iOS ' + version)

    def test_supported_missing_main_preserves_return_and_diagnostic(self):
        with tempfile.TemporaryDirectory() as directory:
            missing = str(Path(directory) / 'Photos.sqlite')
            for files in [[], [missing], [missing + '-wal']]:
                for version in ['14.0', '18.3.2', '26.0']:
                    with self.subTest(files=files, version=version):
                        context = SimpleNamespace(
                            get_files_found=lambda files=files: files,
                            get_report_folder=lambda: directory)
                        with patch.object(parser.iOS, 'get_version', return_value=version), \
                                patch.object(parser, 'logfunc') as logger, \
                                patch.object(parser, 'null_absent_columns') as compiler, \
                                patch.object(parser, 'get_sqlite_db_records') as reader:
                            result = parser.Ph050_2AssetIntResouSyndPL.__wrapped__(context)
                        self.assertEqual(result, ((), [], missing if files == [missing] else None))
                        compiler.assert_not_called()
                        reader.assert_not_called()
                        logger.assert_called_once_with(
                            'Photos.sqlite not found for iOS version ' + version)


if __name__ == '__main__':
    unittest.main()
