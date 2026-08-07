"""Guard the CloudKit artifacts against NoteStore.sqlite files that carry no schema.

iOS keeps zero-byte NoteStore.sqlite placeholders under
group.com.apple.notes/Backups/<date>/, and the artifact's '*NoteStore.sqlite*' path
glob matches them. sqlite3 opens a zero-byte file happily as an empty database, so the
first SELECT raised `no such table: ZICCLOUDSYNCINGOBJECT` and aborted both artifacts
before the real NoteStore.sqlite in the same extraction was ever read - the examiner got
no CloudKit shares at all, only a parsing error in the log. Deleting the backup files by
hand was the only workaround.

scripts/artifacts/notes.py already guards its own queries with does_table_exist_in_db();
these tests hold cloudkitSharing.py to the same contract.
"""
import pathlib
import sqlite3
import shutil
import sys
import tempfile
import unittest
from unittest import mock

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts.artifacts.cloudkitSharing import (  # pylint: disable=wrong-import-position
    cloudkit_participants, cloudkit_sharing)
from scripts.context import Context  # pylint: disable=wrong-import-position


class TestCloudkitSharingMissingTable(unittest.TestCase):
    """A NoteStore.sqlite without ZICCLOUDSYNCINGOBJECT must be skipped, not fatal."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.empty_db = pathlib.Path(self.tmpdir) / 'Backups' / '2026-07-18' / 'NoteStore.sqlite'
        self.empty_db.parent.mkdir(parents=True)
        self.empty_db.touch()  # the zero-byte placeholder iOS leaves behind

        self.populated_db = pathlib.Path(self.tmpdir) / 'NoteStore.sqlite'
        db = sqlite3.connect(self.populated_db)
        db.execute('CREATE TABLE ZICCLOUDSYNCINGOBJECT '
                   '(Z_PK INTEGER, ZIDENTIFIER TEXT, ZSERVERRECORDDATA BLOB, '
                   'ZSERVERSHAREDATA BLOB)')
        db.commit()
        db.close()

        Context.clear()
        Context.set_report_folder(self.tmpdir)
        Context.set_files_found([str(self.empty_db), str(self.populated_db)])

    def tearDown(self):
        Context.clear()
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_zero_byte_notestore_really_has_no_table(self):
        """Documents the trap: the placeholder opens fine, then the SELECT fails."""
        db = sqlite3.connect(f'file:{self.empty_db}?mode=ro', uri=True)
        with self.assertRaises(sqlite3.OperationalError):
            db.execute('SELECT Z_PK FROM ZICCLOUDSYNCINGOBJECT')
        db.close()

    def test_sharing_skips_notestore_without_the_table(self):
        _headers, data_list, _source = cloudkit_sharing.__wrapped__(Context)
        self.assertEqual(data_list, [])

    def test_participants_skips_notestore_without_the_table(self):
        _headers, data_list, _source = cloudkit_participants.__wrapped__(Context)
        self.assertEqual(data_list, [])

    def _skip_messages(self, processor):
        """Run a processor and return only its 'skipped' log lines."""
        with mock.patch('scripts.artifacts.cloudkitSharing.logfunc') as logged:
            processor.__wrapped__(Context)
        return [call.args[0] for call in logged.call_args_list
                if 'no ZICCLOUDSYNCINGOBJECT table' in call.args[0]]

    def test_sharing_logs_the_file_it_skipped(self):
        """Skipping silently would hide a damaged db, so the skip has to be visible."""
        messages = self._skip_messages(cloudkit_sharing)
        self.assertEqual(len(messages), 1)
        self.assertIn(str(self.empty_db), messages[0])
        self.assertIn('(0 bytes)', messages[0])

    def test_participants_logs_the_file_it_skipped(self):
        messages = self._skip_messages(cloudkit_participants)
        self.assertEqual(len(messages), 1)
        self.assertIn(str(self.empty_db), messages[0])

    def test_the_real_database_is_never_reported_as_skipped(self):
        messages = self._skip_messages(cloudkit_sharing)
        self.assertNotIn(str(self.populated_db), ' '.join(messages))

    def test_a_truncated_database_is_logged_with_its_real_size(self):
        """The case the log line exists for: not a placeholder, a damaged database.

        A zero-byte skip is routine, but a NoteStore.sqlite with real bytes in it and
        no schema means the examiner lost data they should know about. The size is in
        the message so the two are distinguishable at a glance in the run log.
        """
        truncated = pathlib.Path(self.tmpdir) / 'Backups' / '2026-07-19' / 'NoteStore.sqlite'
        truncated.parent.mkdir(parents=True)
        truncated.write_bytes(b'SQLite format 3\x00' + b'\x00' * 100)
        Context.set_files_found([str(truncated)])

        messages = self._skip_messages(cloudkit_sharing)
        self.assertEqual(len(messages), 1)
        self.assertIn('(116 bytes)', messages[0])


if __name__ == '__main__':
    unittest.main()
